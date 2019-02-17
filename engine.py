import pygame
import math
from vector import *
from camera import cam
from graph import *
from random import randint

pygame.init()

xres = 1280
yres = 720
display = pygame.display.set_mode((xres,yres))
colors = {"black":(0,0,0),"white":(255,255,255),"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"grey":(211,211,211)}
nikon = cam(vector([0,0,0]),2.5,xres,yres,0.1,100,display)

'''
def p(t):
	return vector(0,math.cos(t),0)+vector(0,0,15)
def r(t):
	return arbitrary_rotation(vector(0,1,0),t/10.0)
'''
cube = graph(vector([0,0,25]))
wave = 0
t = 0

def read_obj(file_name,origin):
	global nikon, xres, colors
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
		mesh.add_tri([vector(vertices[tri[0]]),vector(vertices[tri[1]]),vector(vertices[tri[2]])],colors["green"])
	return mesh
	

def assign_wave():
	global wave
	wave = read_obj("bunny2.obj",vector([0,0,25]))
	print(wave.count)

def draw_wave():
	global nikon, xres, wave, display,t
	wave.transform(vector([0,0,0]).scale(0.1),vector([0,1,1]),0.01)
	nikon.draw_obj(wave)

	t += 0.1	
def assign_cube():
	global nikon, xres, cube, colors
	cube.add_tri([vector([-1,-1,1]),vector([1,-1,1]),vector([1,1,1])],colors["blue"])
	cube.add_tri([vector([-1,-1,1]),vector([1,1,1]),vector([-1,1,1])],colors["blue"])
	cube.add_tri([vector([1,-1,1]),vector([1,-1,-1]),vector([1,1,-1])],colors["green"])
	cube.add_tri([vector([1,-1,1]),vector([1,1,-1]),vector([1,1,1])],colors["black"])
	cube.add_tri([vector([1,-1,-1]),vector([-1,-1,-1]),vector([-1,1,-1])],colors["black"])
	cube.add_tri([vector([1,-1,-1]),vector([-1,1,-1]),vector([1,1,-1])],colors["green"])
	cube.add_tri([vector([-1,-1,-1]),vector([-1,-1,1]),vector([-1,1,1])],colors["red"])
	cube.add_tri([vector([-1,-1,-1]),vector([-1,1,1]),vector([-1,1,-1])],colors["red"])
	cube.add_tri([vector([-1,1,1]),vector([1,1,1]),vector([1,1,-1])],colors["yellow"])
	cube.add_tri([vector([-1,1,1]),vector([1,1,-1]),vector([-1,1,-1])],colors["blue"])
	cube.add_tri([vector([1,-1,1]),vector([-1,-1,-1]),vector([1,-1,-1])],colors["red"])
	cube.add_tri([vector([1,-1,1]),vector([-1,-1,1]),vector([-1,-1,-1])],colors["yellow"])
			
def draw_cube():
	global nikon, xres, cube, display,t
	cube.transform(vector([math.cos(t),math.sin(t),math.sin(t)]).scale(0.1),vector([0,1,1]).direction(),0.03)
	for tri in cube.data:
		if ((tri.normal*((nikon.origin-tri.data[0]).direction())) > 0):
			projection_1 = nikon.project(tri.data[0])
			projection_2 = nikon.project(tri.data[1])
			projection_3 = nikon.project(tri.data[2])

			if ((projection_1 != -1) and (projection_2 != -1) and (projection_3 != -1)):
				pygame.draw.polygon(display,tri.color,[projection_1,projection_2,projection_3],0)
	t += 0.1


pygame.display.set_caption("SAIengine")
#pygame.mouse.set_visible(False)
#pygame.event.set_grab(True)
clock = pygame.time.Clock()
crashed = False
mouse_motion = (0,0)
assign_cube()
assign_wave()
i = 0.01
while not crashed:
	display.fill(colors["white"])
	'''
	mouse = pygame.mouse.get_pos()
	keys = pygame.key.get_pressed()
	nikon.rotate_x(0.4*mouse_motion[0]/(xres+0.0))
	nikon.rotate_y(0.4*mouse_motion[1]/(yres+0.0))
	if keys[pygame.K_UP]:
		nikon.translate(nikon.plane_normal.scale(0.07))
	if keys[pygame.K_DOWN]:
		nikon.translate(nikon.plane_normal.scale(-0.07))
	if keys[pygame.K_LEFT]:
			nikon.translate(nikon.xaxis.scale(-0.07))
	if keys[pygame.K_RIGHT]:
			nikon.translate(nikon.xaxis.scale(0.07))
	
	for event in pygame.event.get():
		if event.type == pygame.MOUSEMOTION:
			mouse_motion = pygame.mouse.get_rel()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				crashed = True
	'''
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			crashed = True
	#print(clock.get_fps())
	#draw_cube()
	draw_wave()
	nikon.pop()
	pygame.display.update()
	if (i <100):
		nikon.move(vector([0,0,0]), i, vector([0,1,0]))
	#print(nikon.zaxis.numerical())
	clock.tick(60)
	#i += 0.01
pygame.quit()
