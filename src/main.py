import math
import numpy

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from PIL import Image

fire_gun_img = Image.open('./sprites/shoot.png')
fire_gun = numpy.asarray(fire_gun_img)

idle_gun_img = Image.open('./sprites/shoot_idle.png')
idle_gun = numpy.asarray(idle_gun_img)

display = (1024, 512)

class World:
    
    def __init__(self, width, height, tile_size, world_map):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.world_map = world_map

class Player:

    def __init__(self, x, y, fov, angle, movement_speed, turning_speed):
        self.x = x
        self.y = y
        self.fov = fov
        self.angle = angle
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed
        self.halfFOV = fov / 2
        self.isFiring = False
        self.health = 100

world_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

world = World(512, 512, 64, world_map)
player = Player(100, 100, 60, 90, 10, 10)

angle_between_subsequent_columns = player.fov / world.width
distance_to_projection_plane = (world.width / 2) / math.tan(math.radians(player.halfFOV))

def raycast(angle):
    horizontal_hit = False
    vertical_hit = False

    # horizontal case
    if not ((angle > 0) and (angle < math.pi)): # angle is facing up
        intersection_y = ((player.y // world.tile_size) * world.tile_size) - 0.01
        ya = -world.tile_size
    else:
        intersection_y = ((player.y // world.tile_size) * world.tile_size) + world.tile_size
        ya = world.tile_size

    intersection_x = ((intersection_y - player.y) / math.tan(angle)) + player.x
    xa = ya / math.tan(angle)
    
    while (not horizontal_hit) and (intersection_x <= world.width and intersection_x >= 0 and intersection_y <= world.height and intersection_y >= 0):
        horizontal_map_x = int(intersection_x // world.tile_size)
        horizontal_map_y = int(intersection_y // world.tile_size)
    
        if world_map[horizontal_map_y][horizontal_map_x]:
            horizontal_hit = True
            horizontalHitPos = [intersection_x, intersection_y]
        else:
            intersection_x += xa
            intersection_y += ya

    # vertical case
    if (angle < 0.5 * math.pi) or (angle > 1.5 * math.pi):
        intersection_x = ((player.x // world.tile_size) * world.tile_size) + world.tile_size
        xa = world.tile_size
    else:
        intersection_x = ((player.x // world.tile_size) * world.tile_size) - 0.01
        xa = -world.tile_size

    intersection_y = ((intersection_x - player.x) * math.tan(angle)) + player.y
    ya = xa * math.tan(angle)

    while (not vertical_hit) and (intersection_x <= world.width and intersection_x >= 0 and intersection_y <= world.height and intersection_y >= 0):
        vertical_map_x = int(intersection_x // world.tile_size)
        vertical_map_y = int(intersection_y // world.tile_size)
    
        if world_map[vertical_map_y][vertical_map_x]:
            vertical_hit = True
            verticalHitPos = [intersection_x, intersection_y]
        else:
            intersection_x += xa
            intersection_y += ya
    
    # distance calc
    if horizontal_hit:
        horizontalDistance = math.sqrt(math.pow(horizontalHitPos[0] - player.x, 2) + math.pow(horizontalHitPos[1] - player.y, 2))
    
    if vertical_hit:
        verticalDistance = math.sqrt(math.pow(verticalHitPos[0] - player.x, 2) + math.pow(verticalHitPos[1] - player.y, 2))
    
    if horizontal_hit and vertical_hit:
        if(horizontalDistance < verticalDistance):
            draw_ray(horizontalHitPos[0], horizontalHitPos[1])
            returned_distance = horizontalDistance
            strip_color = (0.9, 0, 0, 1)
        else:
            draw_ray(verticalHitPos[0], verticalHitPos[1])
            returned_distance = verticalDistance
            strip_color = (0.8, 0, 0, 1)
            
    elif horizontal_hit:
        draw_ray(horizontalHitPos[0], horizontalHitPos[1])
        returned_distance = horizontalDistance
        strip_color = (0.9, 0, 0, 1)
    elif vertical_hit:
        draw_ray(verticalHitPos[0], verticalHitPos[1])
        returned_distance = verticalDistance
        strip_color = (0.8, 0, 0, 1)
    
    return returned_distance, strip_color

def render(col, distance_to_slice, color=(0.9, 0, 0, 1)):
    projected_slice_height = (world.tile_size / distance_to_slice) * distance_to_projection_plane
    glBegin(GL_LINES)
    glColor(0, 0, 0, 1)
    glVertex2d(col + world.width, 0)
    glVertex2d(col + world.width, (world.height / 2) - (projected_slice_height / 2))

    glColor(color)
    glVertex2d(col + world.width, (world.height / 2) - (projected_slice_height / 2))
    glVertex2d(col + world.width, (world.height / 2) + (projected_slice_height / 2))
    
    glColor(0.5, 0.5, 0.5, 1)
    glVertex2d(col + world.width, (world.height / 2) + (projected_slice_height / 2))
    glVertex2d(col + world.width, world.height)
    glEnd()

def display_map(world_map):
    glBegin(GL_QUADS)
    for i in range(0, len(world_map) * world.tile_size, world.tile_size):
        for j in range(0, len(world_map[i // world.tile_size]) * world.tile_size, world.tile_size):
            if world_map[i // world.tile_size][j // world.tile_size]:
                glColor(1, 1, 1, 1)
            else:
                glColor(0, 0, 0, 1)
            glVertex2d(j, i)
            glVertex2d(j, i + world.tile_size)
            glVertex2d(j + world.tile_size, i  + world.tile_size)
            glVertex2d(j + world.tile_size, i)
    glEnd()

def draw_player(player):
    glPointSize(16)
    glColor(1, 0, 0, 1)
    glBegin(GL_POINTS)
    glVertex2d(player.x, player.y)
    glEnd()

def draw_ray(x, y):
    glBegin(GL_LINES)
    glColor(0.3, 0.3, 0.3, 1)
    glVertex2d(player.x, player.y)
    glVertex2d(x, y)
    glEnd()

def render_texture(texture, posX, posY):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPointSize(1.0)
    glBegin(GL_POINTS)
    for i in range(numpy.shape(texture)[0]):
        for j in range(numpy.shape(texture)[1]):
            glColor4f(texture[i][j][0] / 255, texture[i][j][1] / 255, texture[i][j][2] / 255, texture[i][j][3] / 255)
            glVertex2d(world.width + posX + j, posY + i)
    glEnd()

def handlePlayerMovement():
    keys = pygame.key.get_pressed()

    new_x = 0
    new_y = 0

    if keys[K_RIGHT]:
        new_x += (-math.sin(math.radians(player.angle)) *  player.movement_speed)
        new_y += (math.cos(math.radians(player.angle)) * player.movement_speed)
    if keys[K_LEFT]:
        new_x += (math.sin(math.radians(player.angle)) *  player.movement_speed)
        new_y -= (math.cos(math.radians(player.angle)) * player.movement_speed)
    if keys[K_UP]:
        new_x += (math.cos(math.radians(player.angle)) *  player.movement_speed)
        new_y += (math.sin(math.radians(player.angle)) * player.movement_speed)
    if keys[K_DOWN]:
        new_x -= (math.cos(math.radians(player.angle)) *  player.movement_speed)
        new_y -= (math.sin(math.radians(player.angle)) * player.movement_speed)
    
    new_map_x = math.floor((player.x + new_x) / world.tile_size)
    new_map_y = math.floor((player.y + new_y) / world.tile_size)
    if world_map[new_map_y][new_map_x] != 1:
        player.x += new_x
        player.y += new_y

    if keys[K_SPACE]:
        player.isFiring = True
    else:
        player.isFiring = False

    if keys[K_z]:
        player.angle -= player.turning_speed
    if keys[K_x]:
        player.angle += player.turning_speed

def main():
    pygame.init()
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluOrtho2D(0, display[0], display[1], 0)  # left, right, bottom, up

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        handlePlayerMovement()
            
        glClear(GL_COLOR_BUFFER_BIT)
        
        display_map(world_map)
        draw_player(player)

        col = 0
        for angle in numpy.arange(player.angle - (player.halfFOV), player.angle + (player.halfFOV), angle_between_subsequent_columns):
            angle = math.radians(angle)
            angle = angle % (2 * math.pi)
            if angle <= 0:
                angle = (2 * math.pi) + angle
            distance_to_slice, color = raycast(angle)
            render(col, distance_to_slice * math.cos(math.radians(player.angle) - angle), color)
            col += 1

        if(player.isFiring):
            render_texture(fire_gun, (world.width / 2) - (world.tile_size / 2), world.height - world.tile_size)
        else:
            render_texture(idle_gun, (world.width / 2) - (world.tile_size / 2), world.height - world.tile_size)

        pygame.display.flip()
        pygame.time.wait(10)

main()