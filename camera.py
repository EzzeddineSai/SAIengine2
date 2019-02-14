import math
from vector import *
import pygame
class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax,display):
		self.zmin = zmin
		self.zmax = zmax
		self.xres = xres
		self.yres = yres
		self.origin = origin
		self.fov = fov
		self.display = display
		self.buffer = []

	def projection_matrix(self,v_plus):
		a = self.yres/(self.xres+0.0)
		f = 1/math.tan(self.fov/2.0)
		q = self.zmax/(self.zmax-self.zmin+0.0)
		m = np.array([[a*f,0,0,0],
		[0,f,0,0],
		[0,0,q,1],
		[0,0,-1*self.zmin*q,0]])
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
		self.buffer = sorted(self.buffer, key=lambda x:(x.data[0].data[2]+x.data[1].data[2]+x.data[2].data[2])/3.0, reverse=True)
		for tri in self.buffer:
			self.draw_triangle(tri,True)
		self.buffer = []
