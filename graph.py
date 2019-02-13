import math
import numpy as np
from camera import *
from vector import *

class triangle:
	def __init__(self,data,color):
		self.data = data
		self.normal = cross(self.data[1]-self.data[0],self.data[2]-self.data[0]).direction()
		self.color = color

	def translate(self, destination):
		return triangle([self.data[0]+destination,self.data[1]+destination,self.data[2]+destination],self.color)

	def rotate(self,m):
		_p1 = remove_w(vector(np.matmul(m,add_w(self.data[0]).numerical()).tolist()))
		_p2 = remove_w(vector(np.matmul(m,add_w(self.data[1]).numerical()).tolist()))
		_p3 = remove_w(vector(np.matmul(m,add_w(self.data[2]).numerical()).tolist()))
		return triangle([_p1,_p2,_p3],self.color)
	#def reseqeunce(self,orientation):
	#	if (self.normal*orientation < 0):
	#		return triangle([self.p1,self.p3,self.p2],self.color)
	#	else:
	#		return triangle(self.data,self.color)
class graph:
	def __init__(self, origin, displacement=None, rotation=None, mass=0):
		self.origin = origin
		self.mass = 0
		self.time = 0
		self.count = 0
		self.rotator = rotation_matrix(vector([1,0,0]),0)
		self.relative_data = []
		self.data = []

	def transform(self,translation,axis,alpha):
		self.origin = self.origin + translation
		self.rotator= np.matmul(self.rotator,rotation_matrix(axis,alpha))
		self.data = []
		for relative in self.relative_data:
			first = relative.rotate(self.rotator)
			self.data.append(first.translate(self.origin))


	def add_tri(self, vertices, color):
		relative_tri = triangle(vertices,color)
		self.relative_data.append(relative_tri)
		self.data.append(relative_tri.translate(self.origin))
		self.count += 1
	'''
	def update_tri(self,rotator):
		self.data = []
		for relative in self.relative_data:
			rotated = relative.rotate(rotator)
			self.data.append(rotated.translate(self.origin))
	'''
class special: #relative to intial reference frame
	def __init__(self,origin,vilocity):
		self.origin = origin
		self.time = 0.0
		self.vilocity = vilocity
		self.shape = graph(self.origin)
