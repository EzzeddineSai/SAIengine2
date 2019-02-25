import math
import numpy as np
class vector:
	def __init__(self, data):
		self.data = data
		self.components = len(self.data)

	def dim(self):
		return  math.sqrt(sum(i**2 for i in self.data))

	def direction(self):
		return self.scale(1/self.dim())

	def numerical(self):
		return np.array(self.data)

	def update(self, data):
		self.data = data
		self.components = len(self.data)

	def scale(self,c):
		return vector([c*i for i in self.data])

	def __add__(self, v):
		return vector([self.data[i]+v.data[i] for i in range(self.components)])
	def __sub__(self, v):
		return vector([self.data[i]-v.data[i] for i in range(self.components)])
	def __mul__(self, v):
		return sum(self.data[i]*v.data[i] for i in range(self.components))


def get_angle(v1,v2):
    return math.acos((v1*v2)/(v1.dim()*v2.dim()))

def cross(v1,v2):
	return vector([(v1.data[1]*v2.data[2])-(v1.data[2]*v2.data[1]),(v1.data[2]*v2.data[0])-(v1.data[0]*v2.data[2]),(v1.data[0]*v2.data[1])-(v1.data[1]*v2.data[0])])

def scalar_project(v1,v2): #v1 to v2
    return (v1*v2)/(v2.dim())
def vector_project(v1,v2):
	return v2.scale(scalar_project(v1,v2))
def vector_anti_project(v1,v2):	
	return v2-vector_project(v1,v2)
def add_w(v1):
	return vector(v1.data+[1])

def remove_w(v1):
	if (v1.data[3] != 0):
		return vector([v1.data[0],v1.data[1],v1.data[2]]).scale(1/(v1.data[3]+0.0))
	return -1

def metric(v1, v2):
	return (v1-v2).dim()

def rotation_matrix(axis,theta):
	t = 1-math.cos(theta)
	C = math.cos(theta)
	S = math.sin(theta)
	m = np.array([[(t*(axis.data[0]**2))+C,(t*axis.data[0]*axis.data[1])-(S*axis.data[2]),(t*axis.data[0]*axis.data[2])+(S*axis.data[1]),0],
	[(t*axis.data[0]*axis.data[1])+(S*axis.data[2]),(t*(axis.data[1]**2))+C,(t*axis.data[1]*axis.data[2])-(S*axis.data[0]),0],
	[(t*axis.data[0]*axis.data[2])-(S*axis.data[1]),(t*axis.data[1]*axis.data[2])+(S*axis.data[0]),(t*(axis.data[2]**2))+C,0],
	[0,0,0,1]])
	return m