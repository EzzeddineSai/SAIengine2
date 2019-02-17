import math
from vector import *
from graph import *
import pygame
class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax,display,xaxis=vector([1,0,0,1]),yaxis=vector([0,1,0,1])):
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
		self.mini_buffer = []

	def projection_matrix(self,v_plus):#here
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
	
	def push(self, tri):
		self.buffer.append(tri)

	def draw_obj(self, mesh):
		for tri in mesh.data:
			self.clippers(tri)
	
	def pop(self):
		self.buffer = sorted(self.buffer, key=lambda x:(x.data[0].data[2]+x.data[1].data[2]+x.data[2].data[2])/3.0, reverse=True)
		for tri in self.buffer:
			self.draw_triangle(tri,True)
		self.buffer = []

	def move(self, motion, angle, axis):
		self.origin += motion
		rotation =  rotation_matrix(axis,angle)
		self.xaxis = vector(np.matmul(rotation,self.xaxis.numerical()))
		self.yaxis = vector(np.matmul(rotation,self.yaxis.numerical()))
		self.zaxis = add_w(cross(self.xaxis,self.yaxis))
		self.state = np.array([[self.xaxis.data[0],self.yaxis.data[0],self.zaxis.data[0],0],
		[self.xaxis.data[1],self.yaxis.data[1],self.zaxis.data[1],0],
		[self.xaxis.data[2],self.yaxis.data[2],self.zaxis.data[2],0],
		[(remove_w(self.xaxis)*motion)*-1,(remove_w(self.yaxis)*motion)*-1,(remove_w(self.zaxis)*motion)*-1,1]])
	
	def line_intersection(self, v1, v2):
		d = (((self.origin+self.zaxis.scale(self.zmin))-v1)*self.zaxis)/((v2-v1)*(self.zaxis))
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
				self.push(tri)
			
			if (len(outside) == 1):
				v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]])
				v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]])
				self.push(triangle([v1,v2,tri.data[inside[0]]],tri.color).reseqeunce(tri.normal))
				self.push(triangle([v1,v2,tri.data[inside[1]]],tri.color).reseqeunce(tri.normal))
			if (len(outside) == 2):
				data = [0,0,0]
				data[inside[0]] = tri.data[inside[0]]
				data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]])
				data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]])
				self.push(triangle(data,tri.color))
	'''
	def clip_against(self, tri), :
		outside = []
		inside = []
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			for i in range(3):
				if ((tri.data[i]-self.origin+(self.zaxis.scale(self.zmin)))*self.zaxis >= 0):
					inside.append(i)
				else:
					outside.append(i)
			
			if (len(outside) == 0):
				self.push(tri)
			
			if (len(outside) == 1):
				v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]])
				v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]])
				self.push(triangle([v1,v2,tri.data[inside[0]]],tri.color).reseqeunce(tri.normal))
				self.push(triangle([v1,v2,tri.data[inside[1]]],tri.color).reseqeunce(tri.normal))
			if (len(outside) == 3):
				print("outer")
			if (len(outside) == 2):
				data = [0,0,0]
				data[inside[0]] = tri.data[inside[0]]
				data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]])
				data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]])
				self.push(triangle(data,tri.color))
	'''