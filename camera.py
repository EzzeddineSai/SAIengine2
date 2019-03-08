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
		self.forward = (self.origin - self.target).direction()
		self.rightward = cross(self.forward,self.up).direction()
		self.upward = cross(self.rightward,self.forward)

		self.view_matrix =  np.array([
		[self.rightward.data[0],self.rightward.data[1],self.rightward.data[2],(self.rightward*self.origin)*-1],
		[self.upward.data[0],self.upward.data[1],self.upward.data[2],(self.upward*self.origin)*-1],
		[self.forward.data[0],self.forward.data[1],self.forward.data[2],(self.forward*self.origin)*-1],[0,0,0,1]])

		self.projection_matrix = np.array([
		[-1*self.yres/(self.xres+0.0)/math.tan(self.fov/2.0),0,0,0],
		[0,-1/math.tan(self.fov/2.0),0,0],
		[0,0,-1*(self.zmax+self.zmin)/(self.zmax-self.zmin+0.0),(-2*self.zmin*self.zmax/(self.zmax-self.zmin+0.0))],
		[0,0,1,0]]) 

	def refresh(self):
		self.forward = (self.origin - self.target).direction()
		self.rightward = cross(self.forward,self.up).direction()
		self.upward = cross(self.rightward,self.forward)
		self.view_matrix =  np.array([[self.rightward.data[0],self.rightward.data[1],self.rightward.data[2],(self.rightward*self.origin)*-1],
		[self.upward.data[0],self.upward.data[1],self.upward.data[2],(self.upward*self.origin)*-1],
		[self.forward.data[0],self.forward.data[1],self.forward.data[2],(self.forward*self.origin)*-1],[0,0,0,1]])

	def push(self, mesh):
		for polygon in mesh.polygon_data:
			#clip_space = multi_dot([self.projection_matrix , self.view_matrix , mesh.model_matrix])
			camera_space = np.matmul(self.view_matrix, mesh.model_matrix)
			v1 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[0]).numerical())))
			v2 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[1]).numerical())))
			v3 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[2]).numerical())))
			tri = triangle([v1,v2,v3],polygon.color)
			self.buffer.append(tri)

	def depth_sort(self):
		for i in range(len(self.buffer)):
			for j in range(1,len(self.buffer)):
				maximum = max((self.buffer[j-1].data[0].data[2]),(self.buffer[j-1].data[1].data[2]),(self.buffer[j-1].data[2].data[2]))
				minimum = min((self.buffer[j].data[0].data[2]),(self.buffer[j].data[1].data[2]),(self.buffer[j].data[2].data[2]))
				if maximum < minimum:
					temp = self.buffer[j-1]
					self.buffer[j-1] = self.buffer[j]
					self.buffer[j] = temp
	
	def pygame_coord(self, point):
		#return ((self.xres*point.data[0]) + (self.xres/2.0),-1*((self.yres*point.data[1])-(self.yres/2.0)))
		return (((self.xres*point.data[0]) + self.xres)/2.0,((self.yres*point.data[1])-self.yres)/-2.0)

	def draw_frame(self):
		for tri in self.buffer:
			v1 = self.pygame_coord(tri.data[0])
			v2 = self.pygame_coord(tri.data[1])
			v3 = self.pygame_coord(tri.data[2])
			pygame.draw.polygon(self.display,tri.color,[v1,v2,v3],0)
			pygame.draw.lines(self.display,(0,0,0),True,[v1,v2,v3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[v1,v2,v3],1)

	def pop(self):
		#self.zclippers()
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			v1 = save_w(vector(np.matmul(self.projection_matrix,add_w(tri.data[0]).numerical())))
			v2 = save_w(vector(np.matmul(self.projection_matrix,add_w(tri.data[1]).numerical())))
			v3 = save_w(vector(np.matmul(self.projection_matrix,add_w(tri.data[2]).numerical())))
			new_tri = triangle([v1,v2,v3],tri.color)
			if ((tri.normal*tri.data[0]) > 0):
				self.buffer.append(new_tri)
		
		#self.clippers()
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			v1 = remove_w(tri.data[0])
			v2 = remove_w(tri.data[1])
			v3 = remove_w(tri.data[2])
			new_tri = triangle([v1,v2,v3],tri.color)
			self.buffer.append(new_tri)
		
		self.depth_sort()
		self.draw_frame()
		self.buffer = []
		#print(remove_w(vector(np.matmul(self.projection_matrix,np.array([0,0,self.zmin,1])))).numerical())

	def translate(self, displacement):
		self.origin += displacement
		self.target += displacement
		self.refresh()
	
	def rotate(self, angle, axis):
		rotator =  rotation_matrix(axis,angle)
		self.target = self.origin+remove_w(vector(np.matmul(rotator,add_w((self.target- self.origin).direction()).numerical())))
		self.refresh()
	
	def draw_wire(self, mesh):
		for polygon in mesh.polygon_data:
			clip_space = multi_dot([self.projection_matrix() , self.view_matrix() , mesh.model_matrix])
			v1 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[0]).numerical()))))
			v2 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[1]).numerical()))))
			v3 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[2]).numerical()))))
			pygame.draw.lines(self.display,(0,0,0),True,[v1,v2,v3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[v1,v2,v3],1)
		self.refresh()

	def line_intersection(self, v1, v2, normal, point):
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

	def zclippers(self):
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,0,-1]),vector([0,0,self.zmin]))
		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,0,1]),vector([0,0,self.zmax]))

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
			new_tri_1 = triangle([v1,v2,tri.data[inside[0]]],tri.color).resequence(tri.normal)
			if new_tri_1.area.dim() != 0:
				self.buffer.append(new_tri_1)
			new_tri_2 = triangle([v2,tri.data[inside[0]],tri.data[inside[1]]],tri.color).resequence(tri.normal)
			if new_tri_2.area.dim() != 0:	#(255,140,0)
				self.buffer.append(new_tri_2)
			
		if (len(outside) == 2):
			data = [0,0,0]
			data[inside[0]] = tri.data[inside[0]]
			data[outside[0]] = self.line_intersection(tri.data[outside[0]],tri.data[inside[0]],normal, point)
			data[outside[1]] = self.line_intersection(tri.data[outside[1]],tri.data[inside[0]],normal, point)
			new_tri = triangle(data,tri.color).resequence(tri.normal)
			if new_tri.area.dim() != 0:
				self.buffer.append(new_tri)#(255,20,147)