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
		self.dv1 = vector([0,0,0])
		self.dv2 = vector([0,0,0])
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
		j = (self.zmax+self.zmin)/(self.zmax-self.zmin+0.0)
		m = np.array([
		[a*f,0,0,0],
		[0,f,0,0],
		[0,0,-1*j,-2*q*self.zmin],
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

	def push2(self, mesh):
		for polygon in mesh.polygon_data:
			clip_space = multi_dot([self.projection_matrix() , self.view_matrix() , mesh.model_matrix])
			v1 = save_w(vector(np.matmul(clip_space,add_w(polygon.data[0]).numerical())))
			v2 = save_w(vector(np.matmul(clip_space,add_w(polygon.data[1]).numerical())))
			v3 = save_w(vector(np.matmul(clip_space,add_w(polygon.data[2]).numerical())))
			tri = triangle([v1,v2,v3],polygon.color)
			self.buffer.append(tri)
			'''
			if ((tri.normal*((vector([0,0,0])-tri.data[0]).direction())) > 0):
				self.buffer.append(tri)
				print("in",tri.normal.numerical())
				print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
			elif tri.color == (0,255,0):
				print("out",tri.normal.numerical())
				print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
			'''
			#if ((tri.normal*((vector([0,0,0])-tri.data[0]).direction())) > 0):
			#	self.buffer.append(tri)
	def push(self, mesh):
		for polygon in mesh.polygon_data:
			camera_space = multi_dot([self.view_matrix() , mesh.model_matrix])

			v1 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[0]).numerical())))
			v2 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[1]).numerical())))
			v3 = remove_w(vector(np.matmul(camera_space,add_w(polygon.data[2]).numerical())))
			
			tri = triangle([v1,v2,v3],polygon.color)
			#if tri.color == (0,78,100):
			#	print("orig: ",polygon.data[0].numerical(),polygon.data[1].numerical(),polygon.data[2].numerical())
			#	print("camera: ",v1.numerical(),v2.numerical(),v3.numerical())

			if tri.color == (0,78,100):
				self.dv2 = self.pygame_coord(remove_w(save_w(vector(np.matmul(self.projection_matrix(),add_w(tri.normal+v1).numerical())))))
				self.dv1 = self.pygame_coord(remove_w(save_w(vector(np.matmul(self.projection_matrix(),add_w(v1).numerical())))))

			if (tri.normal*(tri.data[0]) > 0) or True:
				#	print("in: ",(tri.data[0]).numerical(),(tri.data[1]).numerical(),(tri.data[2]).numerical(),tri.normal.numerical(),"\n")
				w1 = save_w(vector(np.matmul(self.projection_matrix(),add_w(v1).numerical())))
				w2 = save_w(vector(np.matmul(self.projection_matrix(),add_w(v2).numerical())))
				w3 = save_w(vector(np.matmul(self.projection_matrix(),add_w(v3).numerical())))

				new_tri = triangle([w1,w2,w3],polygon.color)
				#if tri.color == (0,78,100):
				#	print("proj: ",w1.numerical(),w2.numerical(),w3.numerical(),"\n")
				self.buffer.append(new_tri)
			elif tri.color == (0,78,100):
				print("out: ",(tri.data[0]).numerical(),(tri.data[1]).numerical(),(tri.data[2]).numerical(),tri.normal.numerical(),"\n")
			#elif tri.color == (0,78,100):
			#	print("out: ",(vector([0,0,0])-tri.data[0]).direction().numerical(),tri.normal.numerical(),"\n")
			'''
			if tri.color == (0,78,100):
					print("in: ",tri.normal.numerical())
					print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
					print("")
			elif tri.color == (0,78,100):
				print("out: ",tri.normal.numerical())
				print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
				print("")
			'''

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
		return ((self.xres*point.data[0]) + (self.xres/2.0),-1*((self.yres*point.data[1])-(self.yres/2.0)))

	def pop(self):
		self.zclippers()

		temp = self.buffer
		self.buffer = []
		for tri in temp:
			new_tri = triangle([remove_w(tri.data[0]),remove_w(tri.data[1]),remove_w(tri.data[2])],tri.color)
			if ((new_tri.normal*vector([0,0,1])) < 0):
				self.buffer.append(new_tri)

		'''
		if ((new_tri.normal*((vector([0,0,0])-new_tri.data[0]).direction())) > 0):
			self.buffer.append(new_tri)
		elif tri.color == (0,255,0):
			print(str(i)+": ",new_tri.normal.numerical())
			print(new_tri.data[0].numerical(),new_tri.data[1].numerical(),new_tri.data[2].numerical())
			print("")
			i += 1
		'''
		#if ((tri.normal*((vector([0,0,0])-tri.data[0]).direction())) > 0):
		#	self.buffer.append(new_tri)
				
		self.depth_sort()
		self.clippers()
		for tri in self.buffer:
			v1 = self.pygame_coord(tri.data[0])
			v2 = self.pygame_coord(tri.data[1])
			v3 = self.pygame_coord(tri.data[2])
			pygame.draw.polygon(self.display,tri.color,[v1,v2,v3],0)
			pygame.draw.lines(self.display,(0,0,0),True,[v1,v2,v3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[v1,v2,v3],1)
		pygame.draw.lines(self.display,(200,200,60),True,[self.dv1,self.dv2],6)
		#n = self.pygame_coord(tri.normal+tri.data[0])
		#pygame.draw.lines(self.display,(0,0,0),True,[v1,n],6)
		#print(self.buffer[0].data[0].numerical(),self.buffer[0].data[1].numerical(),self.buffer[0].data[2].numerical())

		self.buffer = []
	def translate(self, displacement):
		self.origin += displacement
		self.target += displacement

	def rotate(self, angle, axis):
		#ap = remove_w(vector(np.matmul(self.view_matrix(),add_w(axis).numerical())))
		rotator =  rotation_matrix(axis,angle)
		self.target = self.origin+remove_w(vector(np.matmul(rotator,add_w((self.target- self.origin).direction()).numerical())))
	def draw_wire(self, mesh):
		for polygon in mesh.polygon_data:
			clip_space = multi_dot([self.projection_matrix() , self.view_matrix() , mesh.model_matrix])
			v1 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[0]).numerical()))))
			v2 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[1]).numerical()))))
			v3 = self.pygame_coord(remove_w(vector(np.matmul(clip_space,add_w(polygon.data[2]).numerical()))))
			pygame.draw.lines(self.display,(0,0,0),True,[v1,v2,v3],5)
			pygame.draw.lines(self.display,(255,255,255),True,[v1,v2,v3],1)

	def line_intersection(self, v1, v2, normal,point):
		d = (((point)-v2)*normal)/((v2-v1)*(normal))
		pnt = ((v2-v1).scale(d))+v2
		#if (pnt.data[0] > 1) or (pnt.data[1] > 1) or (pnt.data[2] > 1):
		#	print(v1.numerical(), v2.numerical(),pnt.numerical())
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
			self.clip_against(tri, vector([0,0,1]),vector([0,0,self.zmin]))

		temp = self.buffer
		self.buffer = []
		for tri in temp:
			self.clip_against(tri, vector([0,0,-1]),vector([0,0,self.zmax]))

	def clip_against(self, tri, normal, point):
		outside = []
		inside = []
		for i in range(3):
			if ((tri.data[i]-point)*normal > 0):
				inside.append(i)
			else:
				outside.append(i)
					
		
		if (len(outside) == 0):
			#if (tri.data[0].dim() > 3) or (tri.data[1].dim() > 3) or (tri.data[2].dim() > 3):
			#	print("WRONG")
			#	print((tri.data[0]-point)*normal,(tri.data[1]-point)*normal,(tri.data[2]-point)*normal)
			#	print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
			#	print("")
			self.buffer.append(tri)

		if (len(outside) == 1):
			#print(tri.data[0].numerical(),tri.data[1].numerical(),tri.data[2].numerical())
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
			#print(new_tri.data[0].numerical(),new_tri.data[1].numerical(),new_tri.data[2].numerical())