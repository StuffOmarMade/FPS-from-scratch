import math
import numpy

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

class World:
    
    def __init__(self, width, height, tile_size, world_map):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.world_map = world_map

class Player:

    def __init__(self, height, x, y, fov, angle, movement_speed, turning_speed):
        self.height = height
        self.x = x
        self.y = y
        self.fov = fov
        self.angle = angle
        self.movement_speed = movement_speed
        self.turning_speed = turning_speed
        self.halfFOV = fov / 2

world_map = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

world = World(512, 512, 64, world_map)
player = Player(32, 100, 100, 60, 90, 10, 10)

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
            return horizontalDistance
        else:
            draw_ray(verticalHitPos[0], verticalHitPos[1])
            return verticalDistance
            
    elif horizontal_hit:
        draw_ray(horizontalHitPos[0], horizontalHitPos[1])
        return horizontalDistance
    elif vertical_hit:
        draw_ray(verticalHitPos[0], verticalHitPos[1])
        return verticalDistance

def render(col, distance_to_slice):
    projected_slice_height = (world.tile_size / distance_to_slice) * distance_to_projection_plane
    glBegin(GL_LINES)
    # glColor(0, 0, 0, 1)
    # glVertex2d(col + world.width, 0)
    # glVertex2d(col + world.width, (world.height / 2) - (projected_slice_height / 2))

    glColor(149/255, 6/255, 6/255, 1)
    glVertex2d(col + world.width, (world.height / 2) - (projected_slice_height / 2))
    glVertex2d(col + world.width, (world.height / 2) + (projected_slice_height / 2))
    
    # glColor(0.5, 0.5, 0.5, 1)
    # glVertex2d(col + world.width, (world.height / 2) + (projected_slice_height / 2))
    # glVertex2d(col + world.width, world.height)
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

def handlePlayerMovement():
    keys = pygame.key.get_pressed()

    if keys[K_RIGHT]:
        player.x += (-math.sin(math.radians(player.angle)) *  player.movement_speed)
        player.y += (math.cos(math.radians(player.angle)) * player.movement_speed)
    if keys[K_LEFT]:
        player.x += (math.sin(math.radians(player.angle)) *  player.movement_speed)
        player.y -= (math.cos(math.radians(player.angle)) * player.movement_speed)
    if keys[K_UP]:
        player.x += (math.cos(math.radians(player.angle)) *  player.movement_speed)
        player.y += (math.sin(math.radians(player.angle)) * player.movement_speed)
    if keys[K_DOWN]:
        player.x -= (math.cos(math.radians(player.angle)) *  player.movement_speed)
        player.y -= (math.sin(math.radians(player.angle)) * player.movement_speed)

    if keys[K_z]:
        player.angle -= player.turning_speed
    if keys[K_x]:
        player.angle += player.turning_speed

def main():
    pygame.init()
    display = (1024, 512)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluOrtho2D(0, 1024, 512, 0)  # left, right, bottom, up

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
            distance_to_slice = raycast(angle)
            render(col, distance_to_slice * math.cos(math.radians(player.angle) - angle))
            col += 1
        
        pygame.display.flip()
        pygame.time.wait(10)

main()