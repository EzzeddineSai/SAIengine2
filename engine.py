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
	cube.rotate(vector([0.3,1,1.2]).direction(),0.03)
	#cube.transform(vector([math.cos(t),math.sin(t),math.sin(t)]).scale(0.1),vector([0,1,1]).direction(),0.03)
	t += 0.1

count = pygame.joystick.get_count()
xbox_controler = False
for i in range(count):
	joystick = pygame.joystick.Joystick(i)
	if (joystick.get_name() == "Controller (XBOX 360 For Windows)"):
		joystick.init()
		xbox_controler = True
		break

def game_pad(l_sensitivity, r_sensitivity, t_sensitivity):
	global joystick, nikon
	analog_right = joystick.get_axis(4)
	analog_up = joystick.get_axis(3)
	analog_forward = joystick.get_axis(1)
	analog_right_t = joystick.get_axis(0)
	analog_fly = joystick.get_axis(2)
	#print([joystick.get_button(4),joystick.get_button(5),joystick.get_button(6),joystick.get_button(7)])
	if analog_right > 0.2:
		nikon.rotate(r_sensitivity*analog_right*nikon.fov, nikon.up)
	if analog_right < -0.2:
		nikon.rotate(r_sensitivity*analog_right*nikon.fov, nikon.up)
	if analog_up > 0.2:
		nikon.rotate(r_sensitivity*analog_up*nikon.fov, nikon.right(1))
	if analog_up < -0.2:
		nikon.rotate(r_sensitivity*analog_up*nikon.fov, nikon.right(1))
	if 	analog_right_t > 0.2:
		nikon.translate(nikon.right(l_sensitivity*analog_right_t*nikon.fov))
	if 	analog_right_t < -0.2:
		nikon.translate(nikon.right(l_sensitivity *analog_right_t*nikon.fov))
	if 	analog_forward  > 0.2:
		nikon.translate(cross(nikon.up,nikon.right(1)).scale(l_sensitivity *analog_forward*nikon.fov))
	if 	analog_forward < -0.2:
		nikon.translate(cross(nikon.up,nikon.right(1)).scale(l_sensitivity *analog_forward*nikon.fov))
	if analog_fly < -0.2:
		nikon.translate(nikon.up.scale(-1*analog_fly*t_sensitivity))
	if analog_fly > 0.2:
		nikon.translate(nikon.up.scale(-1*analog_fly*t_sensitivity))

def draw_plane():
	global plane, nikon
	nikon.push(plane)

def key_board(keys,sensitivity):
	global nikon
	if keys[pygame.K_RIGHT]:
		#nikon.rotate((0.4*mouse_motion[1])/(yres+0.0), nikon.right(1))
		nikon.rotate(0.05*sensitivity, nikon.up)
	if keys[pygame.K_LEFT]:
		nikon.rotate(-0.05*sensitivity, nikon.up)
	if keys[pygame.K_UP]:
		nikon.rotate(-0.05*sensitivity, nikon.right(1))
	if keys[pygame.K_DOWN]:
		nikon.rotate(0.05*sensitivity, nikon.right(1))
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


#assign_wave()

while not crashed:
	#print([joystick.get_axis(0),joystick.get_axis(1),joystick.get_axis(2),joystick.get_axis(3),joystick.get_axis(4)])

	display.fill(colors["white"])
	mouse = pygame.mouse.get_pos()

	if (xbox_controler):
		game_pad(0.1,0.005,0.2)
	else:
		keys = pygame.key.get_pressed()
		key_board(keys,0.2)
	for event in pygame.event.get():
		if event.type == pygame.MOUSEMOTION:
			mouse_motion = pygame.mouse.get_rel()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				crashed = True
		if event.type == pygame.QUIT:
			crashed = True
	#print(clock.get_fps())
	draw_plane()
	draw_cube(cube1)
	draw_cube(cube2)
	draw_cube(cube3)
	#draw_wave()
	nikon.pop()
	pygame.display.update()
	
	clock.tick(60)
pygame.quit()

#add: depth sort, clipping, fix camera axis, mouse control,  oganising data, index buffers and effiency,