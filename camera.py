import math
from vector import *

class cam:
	def __init__(self,origin,fov,xres,yres,zmin,zmax):
		self.zmin = zmin
		self.zmax = zmax
		self.xres = xres
		self.yres = yres
		self.origin = origin
		self.fov = fov

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