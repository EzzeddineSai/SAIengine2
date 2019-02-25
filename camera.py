import math
from vector import *
from graph import *
import pygame
import numpy as np
import time
from numpy.linalg import multi_dot


class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax,display,xaxis=vector([-1,0,0]),yaxis=vector([0,-1,0])):
		self.zmin = zmin
		self.zmax = zmax
		self.xres = xres
		self.yres = yres
		self.origin = origin	#eye
		self.fov = fov
		self.display = display
		self.buffer = []
		self.xaxis = xaxis
		self.yaxis = yaxis
		self.zaxis = cross(self.xaxis,self.yaxis)
		self.state = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
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
		m = np.array([[a*f,0,0,0],
		[0,f,0,0],
		[0,0,q,1],
		[0,0,-1*self.zmin*q,0]])
		return m

	def project(self, v):
		normalized = multi_dot([self.projection_matrix() , self.view_matrix() , v])
		n = remove_w(vector(normalized))
		return ((self.xres*n.data[0])+(self.xres/2.0),-1*((self.yres*n.data[1])-self.yres/2.0))

	def draw_triangle(self, tri, wireframe=False):
		#if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
		projection_1 = self.project(add_w(tri.data[0]).numerical())
		projection_2 = self.project(add_w(tri.data[1]).numerical())
		projection_3 = self.project(add_w(tri.data[2]).numerical())
		pygame.draw.polygon(self.display,tri.color,[projection_1,projection_2,projection_3],0)
		if wireframe:
			pygame.draw.lines(self.display,(0,0,0),True,[projection_1,projection_2,projection_3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[projection_1,projection_2,projection_3],1)

	def push(self, mesh):
		for polygon in mesh.polygon_data:
			v1 = remove_w(vector(np.matmul(mesh.model_matrix,add_w(polygon.data[0]).numerical())))
			v2 = remove_w(vector(np.matmul(mesh.model_matrix,add_w(polygon.data[1]).numerical())))
			v3 = remove_w(vector(np.matmul(mesh.model_matrix,add_w(polygon.data[2]).numerical())))
			tri = triangle([v1,v2,v3],polygon.color)
			if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
				self.buffer.append(tri)
	
	def depth_sort(self):
		d = (self.origin*self.forward(1))*-1
		for i in range(len(self.buffer)):
			for j in range(i+1,len(self.buffer)):
				i1 = (self.buffer[i].data[0]*self.forward(1))+d
				i2 = (self.buffer[i].data[1]*self.forward(1))+d
				i3 = (self.buffer[i].data[2]*self.forward(1))+d
				maximum = max(i1,i2,i3)
				j1 = (self.buffer[j].data[0]*self.forward(1))+d
				j2 = (self.buffer[j].data[1]*self.forward(1))+d
				j3 = (self.buffer[j].data[2]*self.forward(1))+d
				minimum = min(j1,j2,j3)
				#print([maximum,minimum])
				if maximum < minimum:
					temp = self.buffer[i]
					self.buffer[i] = self.buffer[j]
					self.buffer[j] = temp
	
	def pop(self):
		#xplane_left = remove_w(vector(np.matmul(rotation_matrix(self.yaxis,self.fov/2.0),add_w(self.xaxis).numerical()))).scale(-1)
		#xplane_right = remove_w(vector(np.matmul(rotation_matrix(self.yaxis,-self.fov/2.0),add_w(self.xaxis).numerical())))
		#zplane = self.zaxis
		#temp = self.buffer

		#self.buffer = []
		#for tri in temp:
		#	self.clip_against(tri, xplane_left)
		#temp = self.buffer
		
		#self.buffer = []
		#for tri in temp:
		#	self.clip_against(tri, xplane_right)
		#temp = self.buffer
		
		#self.buffer = []
		#for tri in temp:
		#	self.clippers(tri)
		#for tri in temp:
		#self.buffer = sorted(self.buffer, key=lambda x:min(metric(x.data[0],self.origin),metric(x.data[1],self.origin),metric(x.data[2],self.origin)), reverse=True)
		self.depth_sort()
		for tri in self.buffer:
			self.draw_triangle(tri,True)
		self.buffer = []
	def translate(self, displacement):
		self.origin += displacement
		self.target += displacement

	def rotate(self, angle, axis):
		#ap = remove_w(vector(np.matmul(self.view_matrix(),add_w(axis).numerical())))
		rotator =  rotation_matrix(axis,angle)
		self.target = self.origin+remove_w(vector(np.matmul(rotator,add_w((self.target- self.origin).direction()).numerical())))
	
	def line_intersection(self, v1, v2, normal):
		d = (((self.origin+self.zaxis.scale(self.zmin))-v2)*normal)/((v2-v1)*(normal))
		pnt = ((v2-v1).scale(d))+v2
		return pnt
	
	def clippers(self,tri):
		outside = []
		inside = []
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			for i in range(3):
				if ((tri.data[i]-(self.origin+self.zaxis.scale(self.zmin)))*self.zaxis > 0):
					inside.append(i)
				else:
					outside.append(i)
			
			if (len(outside) == 0):
				self.buffer.append(tri)
			'''
			if (len(outside) == 1):
				v1 = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],self.zaxis)
				v2 = self.line_intersection(tri.data[outside[0]],tri.data[inside[1]],self.zaxis)
				
				try:
					print("promo")
					self.buffer.append(triangle([v1,v2,tri.data[inside[0]]],tri.color).reseqeunce(tri.normal))
					self.buffer.append(triangle([v1,v2,tri.data[inside[1]]],tri.color).reseqeunce(tri.normal))
				except:
					#pass
					print("no")
					#print((tri.data[inside[0]]-tri.data[outside[0]]).numerical(),(tri.data[inside[1]]-tri.data[outside[0]]).numerical(),self.zaxis.numerical())
			if (len(outside) == 2):
				data = [0,0,0]
				data[inside[0]] = tri.data[inside[0]]
				data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],self.zaxis)
				data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]],self.zaxis)
				self.buffer.append(triangle(data,tri.color))
				print("nono")
			'''
	def clip_against(self, tri, normal):
		outside = []
		inside = []
		if ((tri.normal*((self.origin-tri.data[0]).direction())) > 0):
			for i in range(3):
				if ((tri.data[i]-self.origin+(self.zaxis.scale(self.zmin)))*normal > 0):
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