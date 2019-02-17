import math
from vector import *
from graph import *
import pygame
class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax,display,xaxis=vector([-1,0,0]),yaxis=vector([0,-1,0])):
		self.zmin = zmin
		self.zmax = zmax
		self.xres = xres
		self.yres = yres
		self.origin = origin
		self.fov = fov
		self.display = display
		self.buffer = []
		self.xaxis = xaxis
		self.yaxis = yaxis
		self.zaxis = add_w(cross(self.xaxis,self.yaxis))
		self.state = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

	def projection_matrix(self,v_plus):
		a = self.yres/(self.xres+0.0)
		f = 1/math.tan(self.fov/2.0)
		q = self.zmax/(self.zmax-self.zmin+0.0)
		k = np.array([[a*f,0,0,0],
		[0,f,0,0],
		[0,0,q,1],
		[0,0,-1*self.zmin*q,0]])
		m = np.matmul(k,self.state)
		projection = remove_w(vector(np.matmul(m,v_plus.numerical()).tolist()))
		return projection

	def project(self, v):
		normalized = self.projection_matrix(add_w(v))
		return ((self.xres*normalized.data[0])+(self.xres/2.0),-1*((self.yres*normalized.data[1])-self.yres/2.0))

	def draw_triangle(self, tri, wireframe=False):
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			projection_1 = self.project(tri.data[0])
			projection_2 = self.project(tri.data[1])
			projection_3 = self.project(tri.data[2])
			pygame.draw.polygon(self.display,tri.color,[projection_1,projection_2,projection_3],0)
			if wireframe:
				pygame.draw.lines(self.display,(0,0,0),True,[projection_1,projection_2,projection_3],5)
				pygame.draw.lines(self.display,(255,255,255),True,[projection_1,projection_2,projection_3],1)
	
	def push(self, mesh):
		self.buffer += mesh.data

	def pop(self):
		xplane_left = remove_w(vector(np.matmul(rotation_matrix(self.yaxis,self.fov/2.0),add_w(self.xaxis).numerical()))).scale(-1)
		xplane_right = remove_w(vector(np.matmul(rotation_matrix(self.yaxis,-self.fov/2.0),add_w(self.xaxis).numerical())))
		zplane = self.zaxis
		temp = self.buffer

		self.buffer = []
		for tri in temp:
			self.clip_against(tri, xplane_left)
		temp = self.buffer
		
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, xplane_right)
		temp = self.buffer
		
		self.buffer = []
		for tri in temp:
			self.clippers(tri)
		
		self.buffer = sorted(self.buffer, key=lambda x:(x.data[0].data[2]+x.data[1].data[2]+x.data[2].data[2])/3.0, reverse=True)
		for tri in self.buffer:
			self.draw_triangle(tri,True)
		self.buffer = []

	def move(self, motion, angle, axis):
		self.origin += motion
		rotation =  rotation_matrix(axis,angle)
		self.xaxis = remove_w(vector(np.matmul(rotation,add_w(self.xaxis).numerical())))
		self.yaxis = remove_w(vector(np.matmul(rotation,add_w(self.yaxis).numerical())))
		self.zaxis = cross(self.xaxis,self.yaxis)
		self.state = np.array([[self.xaxis.data[0],self.yaxis.data[0],self.zaxis.data[0],(self.xaxis*self.origin)*-1],
		[self.xaxis.data[1],self.yaxis.data[1],self.zaxis.data[1],(self.yaxis*self.origin)*-1],
		[self.xaxis.data[2],self.yaxis.data[2],self.zaxis.data[2],(self.zaxis*self.origin)*-1],
		[0,0,0,1]])
	
	def line_intersection(self, v1, v2, normal):
		d = (((self.origin+self.zaxis.scale(self.zmin))-v1)*normal)/((v2-v1)*(normal))
		pnt = ((v2-v1).scale(d))+v1
		return pnt
	
	def clippers(self,tri):
		outside = []
		inside = []
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			for i in range(3):
				if ((tri.data[i]-(self.origin+self.zaxis.scale(self.zmin)))*self.zaxis >= 0):
					inside.append(i)
				else:
					outside.append(i)
			
			if (len(outside) == 0):
				self.buffer.append(tri)
			
			if (len(outside) == 1):
				v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],self.zaxis)
				v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]],self.zaxis)
				self.buffer.append(triangle([v1,v2,tri.data[inside[0]]],tri.color).reseqeunce(tri.normal))
				self.buffer.append(triangle([v1,v2,tri.data[inside[1]]],tri.color).reseqeunce(tri.normal))
			if (len(outside) == 2):
				data = [0,0,0]
				data[inside[0]] = tri.data[inside[0]]
				data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],self.zaxis)
				data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]],self.zaxis)
				self.buffer.append(triangle(data,tri.color))

	def clip_against(self, tri, normal):
		outside = []
		inside = []
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			for i in range(3):
				if ((tri.data[i]-self.origin+(self.zaxis.scale(self.zmin)))*normal >= 0):
					inside.append(i)
				else:
					outside.append(i)
			
			if (len(outside) == 0):
				self.buffer.append(tri)
			
			if (len(outside) == 1):
				v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],normal)
				v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]],normal)
				self.buffer.append(triangle([v1,v2,tri.data[inside[0]]],tri.color).reseqeunce(tri.normal))
				self.buffer.append(triangle([v1,v2,tri.data[inside[1]]],tri.color).reseqeunce(tri.normal))
			if (len(outside) == 2):
				data = [0,0,0]
				data[inside[0]] = tri.data[inside[0]]
				data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],normal)
				data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]],normal)
				self.buffer.append(triangle(data,tri.color)) 