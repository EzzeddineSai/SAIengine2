import math
import numpy as np
from numpy.linalg import multi_dot
from vector import *
class triangle:
	def __init__(self,data,color):
		self.data = data
		self.area = cross(self.data[1]-self.data[0],self.data[2]-self.data[0])
		self.normal = vector([0,1,0])
		if self.area.dim() != 0:
			self.normal = self.area.direction()
		self.color = color
	def resequence(self, target):
		if self.normal*target < 0:
			return triangle([self.data[0],self.data[2],self.data[1]],self.color)
		else:
			return self
class graph:
	def __init__(self, origin):
		self.origin = origin
		self.mass = 0
		self.time = 0
		self.polygons = 0
		self.polygon_data = []	#remove this
		self.scale_matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
		self.rotation_matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
		self.translation_matrix = np.array([[1,0,0,self.origin.data[0]],[0,1,0,self.origin.data[1]],[0,0,1,self.origin.data[2]],[0,0,0,1]])
		self.model_matrix = np.array(self.translation_matrix, copy=True)
		self.vertex_buffer = []
		self.index_buffer = []

	def rotate(self,axis,theta):
		t = 1-math.cos(theta)
		C = math.cos(theta)
		S = math.sin(theta)
		m = np.array([[(t*(axis.data[0]**2))+C,(t*axis.data[0]*axis.data[1])-(S*axis.data[2]),(t*axis.data[0]*axis.data[2])+(S*axis.data[1]),0],
		[(t*axis.data[0]*axis.data[1])+(S*axis.data[2]),(t*(axis.data[1]**2))+C,(t*axis.data[1]*axis.data[2])-(S*axis.data[0]),0],
		[(t*axis.data[0]*axis.data[2])-(S*axis.data[1]),(t*axis.data[1]*axis.data[2])+(S*axis.data[0]),(t*(axis.data[2]**2))+C,0],
		[0,0,0,1]])
		self.rotation_matrix = np.matmul(m,self.rotation_matrix)
		#normalized = 
		self.model_matrix = multi_dot([ self.translation_matrix , self.rotation_matrix , self.scale_matrix])

	def translate(self,displacement):
		m = np.array([[1,0,0,displacement.data[0]],[0,1,0,displacement[1]],[0,0,1,displacement[2]],[0,0,0,1]])
		self.translation_matrix = np.matmul(m,self.translation_matrix )
		self.model_matrix = multi_dot([ self.translation_matrix , self.rotation_matrix , self.scale_matrix])

	def scale(self, scaler):
		self.scale_matrix = np.matmul(np.array([[scaler,0,0,0],[0,scaler,0,0],[0,0,scaler,0],[0,0,0,1]]),self.scale_matrix)
		self.model_matrix = multi_dot([ self.translation_matrix , self.rotation_matrix , self.scale_matrix])

	def add_vertex(self, pos):
		self.vertex_buffer.append(pos)
	
	def add_tri(self, vertices, color):
		self.polygon_data.append(triangle(vertices,color))
		self.polygons += 1