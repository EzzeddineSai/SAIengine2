import math
from vector import *
from graph import *
import pygame
import numpy as np
import time
from numpy.linalg import multi_dot
#z 1 to 0, -0.5 to 0.5

class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax,display):
		self.zmin = zmin
		self.zmax = zmax
		self.xres = xres
		self.yres = yres
		self.origin = origin	#eye
		self.fov = fov
		self.display = display
		self.buffer = []
		self.up = vector([0,1,0])	#for tilt
		self.target = vector([0,0,1])	#point to look

	def view_matrix(self):
		f = (self.origin - self.target).direction()	#direction of viewing
		r = cross(f,self.up).direction()	#right axis
		u = cross(r,f)	#insure up is orthogonal
		m = np.array([[r.data[0],r.data[1],r.data[2],(r*self.origin)*-1],[u.data[0],u.data[1],u.data[2],(u*self.origin)*-1],
		[f.data[0],f.data[1],f.data[2],(f*self.origin)*-1],[0,0,0,1]])
		
		return m
	def right(self,sensitivity):
		f = (self.origin - self.target).direction()	#direction of viewing
		r = cross(f,self.up).direction()
		return r.scale(sensitivity)
	def forward(self,sensitivity):
		f = (self.origin - self.target).direction()
		return f.scale(-1*sensitivity)
	def upwards(self,sensitivity):
		f = (self.origin - self.target).direction()	#direction of viewing
		r = cross(f,self.up).direction()	#right axis
		u = cross(r,f)
		return u.scale(sensitivity)

	def projection_matrix(self):
		a = self.yres/(self.xres+0.0)
		f = 1/math.tan(self.fov/2.0)
		q = self.zmax/(self.zmax-self.zmin+0.0)
		j = (self.zmax+self.zmin)/(-self.zmax+self.zmin+0.0)
		m = np.array([
		[a*f,0,0,0],
		[0,f,0,0],
		[0,0,j,-2*q*self.zmin],
		[0,0,-1,0]]) #self.zmin*
		#[a*f,0,0,0],
		#[0,f,0,0],
		#[0,0,q,1],
		#[0,0,-1*q*self.zmin,0]]) #self.zmin*
		return m

	def project(self, v):
		normalized = multi_dot([self.projection_matrix() , self.view_matrix() , v])
		n = remove_w(vector(normalized))
		return n

	def push(self, mesh):
		for polygon in mesh.polygon_data:
			clip_space = multi_dot([self.projection_matrix() , self.view_matrix() , mesh.model_matrix])
			v1 = remove_w(vector(np.matmul(clip_space,add_w(polygon.data[0]).numerical())))
			v2 = remove_w(vector(np.matmul(clip_space,add_w(polygon.data[1]).numerical())))
			v3 = remove_w(vector(np.matmul(clip_space,add_w(polygon.data[2]).numerical())))
			tri = triangle([v1,v2,v3],polygon.color)
			if ((tri.normal*((vector([0,0,-1])-tri.data[0]).direction())) > 0):
				self.buffer.append(tri)
	
	def depth_sort(self):
		d = (self.origin*self.forward(1))*-1
		for i in range(len(self.buffer)):
			for j in range(1,len(self.buffer)):
				a0 = (self.buffer[j-1].data[0]*self.forward(1))+d
				a1 = (self.buffer[j-1].data[1]*self.forward(1))+d
				a2 = (self.buffer[j-1].data[2]*self.forward(1))+d
				maximum = max(a0,a1,a2)
				b0 = (self.buffer[j].data[0]*self.forward(1))+d
				b1 = (self.buffer[j].data[1]*self.forward(1))+d
				b2 = (self.buffer[j].data[2]*self.forward(1))+d
				minimum = min(b0,b1,b2)
				#print([maximum,minimum])
				if maximum < minimum:
					temp = self.buffer[j-1]
					self.buffer[j-1] = self.buffer[j]
					self.buffer[j] = temp
				#else:
				#	if (self.buffer[i].normal)

	def pygame_coord(self, point):
		return ((self.xres*point.data[0]) + (self.xres/2.0),-1*((self.yres*point.data[1])-(self.yres/2.0)))

	def pop(self):
		a = self.yres/(self.xres+0.0)
		m = -1*math.tan(math.tan(self.fov/2.0)/a)
		self.clippers()

		for tri in self.buffer:
			v1 = self.pygame_coord(tri.data[0])
			v2 = self.pygame_coord(tri.data[1])
			v3 = self.pygame_coord(tri.data[2])
			pygame.draw.polygon(self.display,tri.color,[v1,v2,v3],0)
			pygame.draw.lines(self.display,(0,0,0),True,[v1,v2,v3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[v1,v2,v3],1)
		self.buffer = []
	def translate(self, displacement):
		self.origin += displacement
		self.target += displacement

	def rotate(self, angle, axis):
		#ap = remove_w(vector(np.matmul(self.view_matrix(),add_w(axis).numerical())))
		rotator =  rotation_matrix(axis,angle)
		self.target = self.origin+remove_w(vector(np.matmul(rotator,add_w((self.target- self.origin).direction()).numerical())))
	
	def line_intersection(self, v1, v2, normal,point):
		d = (((point)-v2)*normal)/((v2-v1)*(normal))
		pnt = ((v2-v1).scale(d))+v2
		return pnt
	def clippers(self):
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([-1,0,0]),vector([0.5,0,0]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([1,0,0]),vector([-0.5,0,0]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,-1,0]),vector([0,0.5,0]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,1,0]),vector([0,-0.5,0]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,0,1]),vector([0,0,0]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,0,-1]),vector([0,0,1]))
	def clip_against(self, tri, normal, point):
		outside = []
		inside = []

		for i in range(3):
			if ((tri.data[i]-point)*normal > 0):
				inside.append(i)
			else:
				outside.append(i)
		
		if (len(outside) == 0):
			self.buffer.append(tri)
		
		if (len(outside) == 1):
			v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],normal, point)
			v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]],normal, point)
			new_tri_1 = triangle([v1,v2,tri.data[inside[0]]],(255,140,0)).resequence(tri.normal)
			if new_tri_1.area.dim() != 0:
				self.buffer.append(new_tri_1)
			new_tri_2 = triangle([v2,tri.data[inside[0]],tri.data[inside[1]]],(255,140,0)).resequence(tri.normal)
			if new_tri_2.area.dim() != 0:
				self.buffer.append(new_tri_2)
			#if normal == remove_w(vector(np.matmul(rotation_matrix(self.upwards(1),-1*((math.pi/4.0)-(self.fov/2.0))),add_w(self.forward(1)).numerical()))):
			#(255,140,0)
		if (len(outside) == 2):
			data = [0,0,0]
			data[inside[0]] = tri.data[inside[0]]
			data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],normal, point)
			data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]],normal, point)
			new_tri = triangle(data,(255,20,147)).resequence(tri.normal)
			if new_tri.area.dim() != 0:
				self.buffer.append(new_tri)#(255,20,147)