import pygame
import math
from vector import *
from camera import cam
from graph import *
from random import randint
import time
#model matrix (model to world),  view matrix (world to camera cordinates), projection matrix (camera to perspective)
pygame.init()

xres = 1280
yres = 720
display = pygame.display.set_mode((xres,yres))
colors = {"black":(0,0,0),"white":(255,255,255),"red":(255,0,0),"green":(0,255,0),"blue":(0,0,255),"yellow":(255,255,0),"grey":(211,211,211)}
nikon = cam(vector([0,0,0]),2.5,xres,yres,0.1,100,display)


cube1 = graph(vector([-5,0,25]))
cube2 = graph(vector([5,0,25]))
cube3 = graph(vector([18,0,18]))
plane = graph(vector([0,-1,20]))
plane.add_tri([vector([-1,0,-1]),vector([-1,0,1]),vector([1,0,1])],colors["blue"])
plane.add_tri([vector([-1,0,-1]),vector([1,0,1]),vector([1,0,-1])],colors["blue"])
plane.scale(10)
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
	wave = read_obj("bunny2.obj",vector([0,0,45]))
	print(wave.polygons)

def draw_wave():
	global nikon, xres, wave, display,t
	wave.rotate(vector([0,1,0]),0.03)
	nikon.push(wave)

	t += 0.1	

def assign_cube(cube):
	global nikon, xres, colors
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
			
def draw_cube(cube):
	global nikon, xres, display,t
	nikon.push(cube)
	cube.rotate(vector([0,1,0]),0.03)
	#cube.transform(vector([math.cos(t),math.sin(t),math.sin(t)]).scale(0.1),vector([0,1,1]).direction(),0.03)
	t += 0.1

def draw_plane():
	global plane, nikon
	nikon.push(plane)

pygame.display.set_caption("SAIengine")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
clock = pygame.time.Clock()
crashed = False
mouse_motion = (0,0)
mouse_position = (0,0)
assign_cube(cube1)
assign_cube(cube2)
assign_cube(cube3)

count = pygame.joystick.get_count()
for i in range(count):
	joystick = pygame.joystick.Joystick(i)
	joystick.init()
#assign_wave()
sensitivity = 0.2
while not crashed:
        
	display.fill(colors["white"])

	mouse = pygame.mouse.get_pos()
	keys = pygame.key.get_pressed()
	nikon.rotate((0.4*mouse_motion[1])/(yres+0.0), nikon.right(1))
	nikon.rotate((0.4*mouse_motion[0])/(xres+0.0), nikon.upwards(1))
	if keys[pygame.K_SPACE]:
		nikon.translate(nikon.up.scale(sensitivity))
	if keys[pygame.K_LSHIFT]:
		nikon.translate(nikon.up.scale(-1*sensitivity))

	if keys[pygame.K_a]:
		nikon.translate(nikon.right(-1*sensitivity))
	if keys[pygame.K_d]:
		nikon.translate(nikon.right(sensitivity))
	if keys[pygame.K_w]:
		nikon.translate(cross(nikon.up,nikon.right(-1)).scale(sensitivity))
	if keys[pygame.K_s]:
		nikon.translate(cross(nikon.up,nikon.right(1)).scale(sensitivity))
	for event in pygame.event.get():
		if event.type == pygame.MOUSEMOTION:
			mouse_motion = pygame.mouse.get_rel()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				crashed = True
		if event.type == pygame.QUIT:
			crashed = True
	#print(clock.get_fps())
	#draw_plane()
	draw_cube(cube1)
	draw_cube(cube2)
	draw_cube(cube3)
	#draw_wave()
	nikon.pop()
	pygame.display.update()
	
	clock.tick(60)
pygame.quit()