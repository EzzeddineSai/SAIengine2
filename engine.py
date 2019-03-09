import pygame
import math
from vector import *
from camera import cam
from graph import *
from random import randint
#import time

def read_obj(self,file_name,origin):
	vertices = []
	faces = []
	mesh = graph(origin)
	with open (file_name,'rb') as f:
		for line in f:
			temp1 = line.decode("utf-8")
			if temp1[0] == "v":
				temp2 = temp1.strip("\n")
				temp3 = temp2.split(' ')
				
				vertices.append([float(temp3[1]),float(temp3[2]),float(temp3[3])])
			if temp1[0] == "f":
				temp2 = temp1.strip("\n")
				temp3 = temp2.split(' ')
				faces.append([int(temp3[1])-1,int(temp3[2])-1,int(temp3[3])-1])
	for tri in faces:
		mesh.add_tri([vector(vertices[tri[0]]),vector(vertices[tri[1]]),vector(vertices[tri[2]])],(randint(140,150),randint(170,220),20))
	return mesh	

class renderer:
	def __init__(self,xres,yres,fov,near,far):
	#model matrix (model to world),  view matrix (world to camera cordinates), projection matrix (camera to perspective)
		colors = {"black":(0,0,0),"white":(255,255,255),"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"grey":(211,211,211),"go":(0,78,100)}
		self.running = True
		self.xres = xres
		self.yres = yres
		self.main_camera = cam(vector([0,0,0]),fov,xres,yres,near,far)
		self.xbox_controler = False
		self.joystick = None
		self.object_buffer = {}
		pygame.init()
		self.display = pygame.display.set_mode((xres,yres))
		self.crashed = False
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("SAIengine")
		pygame.mouse.set_visible(False)
		pygame.event.set_grab(True)
		
		count = pygame.joystick.get_count()
		for i in range(count):
			self.joystick = pygame.joystick.Joystick(i)
			if (self.joystick.get_name() == "Controller (XBOX 360 For Windows)"):
				self.joystick.init()
				self.xbox_controler = True
				break
		if not (self.xbox_controler):
			self.joystick = None
		
	def game_pad(self, l_sensitivity, r_sensitivity, t_sensitivity):
		analog_right = self.joystick.get_axis(4)
		analog_up = self.joystick.get_axis(3)
		analog_forward = self.joystick.get_axis(1)
		analog_right_t = self.joystick.get_axis(0)
		analog_fly = self.joystick.get_axis(2)
		if analog_right > 0.2:
			self.main_camera.rotate(r_sensitivity*analog_right, self.main_camera.up)
		if analog_right < -0.2:
			self.main_camera.rotate(r_sensitivity*analog_right, self.main_camera.up)
		if (analog_up > 0.2) and (self.main_camera.forward*self.main_camera.up<0.85):
			self.main_camera.rotate(r_sensitivity*analog_up, self.main_camera.rightward)
		if (analog_up < -0.2) and (self.main_camera.forward*self.main_camera.up.scale(-1)<0.85):
			self.main_camera.rotate(r_sensitivity*analog_up, self.main_camera.rightward)
		if 	analog_right_t > 0.2:
			self.main_camera.translate(self.main_camera.rightward.scale(l_sensitivity*analog_right_t))
		if 	analog_right_t < -0.2:
			self.main_camera.translate(self.main_camera.rightward.scale(l_sensitivity *analog_right_t))
		if 	analog_forward  > 0.2:
			self.main_camera.translate(cross(self.main_camera.up,self.main_camera.rightward.scale(l_sensitivity*analog_forward)))
		if 	analog_forward < -0.2:
			self.main_camera.translate(cross(self.main_camera.up,self.main_camera.rightward.scale(l_sensitivity*analog_forward)))
		if analog_fly < -0.2:
			self.main_camera.translate(self.main_camera.up.scale(-1*analog_fly*t_sensitivity))
		if analog_fly > 0.2:
			self.main_camera.translate(self.main_camera.up.scale(-1*analog_fly*t_sensitivity))
	
	def add_obj(self,mesh,name):
		if (name not in self.object_buffer):
			self.object_buffer[name] = mesh

	def display_triangle(self,tri):
		v1 = (((self.xres*tri.data[0].data[0]) + self.xres)/2.0,((self.yres*tri.data[0].data[1])-self.yres)/-2.0)
		v2 = (((self.xres*tri.data[1].data[0]) + self.xres)/2.0,((self.yres*tri.data[1].data[1])-self.yres)/-2.0)
		v3 = (((self.xres*tri.data[2].data[0]) + self.xres)/2.0,((self.yres*tri.data[2].data[1])-self.yres)/-2.0)
		pygame.draw.polygon(self.display,tri.color,[v1,v2,v3],0)

	def run_frame(self):
		if not self.crashed:
			self.display.fill((255,255,255))
			if (self.xbox_controler):
				self.game_pad(0.1,0.01,0.07)
			
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.crashed = True
				if event.type == pygame.QUIT:
					self.crashed = True
			
			for name, mesh in self.object_buffer.items():
				self.main_camera.push(mesh)
			for tri in self.main_camera.pop():
				self.display_triangle(tri)
			pygame.display.update()
			print(self.clock.get_fps())
			self.clock.tick(60)
			return True
		
		else:
			pygame.quit()
			return False