import pyTGA
import math
import numpy
from stb import image as im

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

width = 512
height = 512
block_size = 32

player_x = 40
player_y = 64
player_size = 8

player_a = 40
fov = 60
fov_rad = math.radians(fov)

distance_to_projection_plane = (width / 2) / math.tan(fov_rad / 2)

world_map = [[0 for i in range(int(height / block_size))] for j in range(int(width / block_size))]

block_list = [
    [1, 6],
    [1, 7],
    [1, 8],
    [1, 9],
    [1, 10],
    [1, 11],

    [2, 5],
    [3, 5],
    [4, 5],

    [5, 3],
    [5, 4],
    [5, 5],
    [5, 6],
    [5, 7],

    [6, 3],
    [7, 3],
    [8, 3],

    [6, 7],
    [7, 7],
    [8, 7],
    [9, 7],
    [10, 7],
    [11, 7],
    [12, 7],
    [13, 7],
    [14, 7],

    [14, 1],
    [14, 2],
    [14, 3],
    [14, 4],
    [14, 5],
    [14, 6],

    [3, 8],
    [3, 9],
    [3, 10],
    [3, 11],
    [3, 12],
    [3, 13],
    [3, 14],
    [3, 15],

    [6, 8],
    [6, 9],
    [6, 10],
    [6, 11],

    [8, 10],
    [8, 11],
    [8, 12],
    [8, 13],
    [8, 14],
    [8, 15]
]

for block in block_list:
        world_map[block[0]][block[1]] = 1

x = im.load('BIGSQUARES.png')

def init_image(width, height, background_color):
    data = [[background_color] * width ] * height
    image = pyTGA.Image(data)

    return image

# frame_buffer = init_image(width, height, (0, 0, 0, 255))
# rendered_img = init_image(width, height, (255, 255, 255, 255))

def set_pixel(x, y, color):
    glBegin(GL_POINTS)
    glColor(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)
    glVertex2f(x, y)
    glEnd()

def draw_block(x, y, size, color):
    for i in range(size):
        for j in range(size):
            set_pixel(j + x, i + y, color)

#def draw_blocks(img):
#    for block in block_list:
#       for i in range(block_size):
#            for j in range(block_size):
#                img.set_pixel(j + (block_size * block[0]), i + (block_size * block[1]), (255, 255, 255, 0))

def single_raycast(col, angle):
        global player_y

        angle_in_rad = math.radians(angle)

        adj = math.cos(angle_in_rad)
        opp = math.sin(angle_in_rad)

        for h in range(0, height, 1):
            pixel_x = (player_x + (player_size / 2)) + (adj * h)
            pixel_y = (player_y + (player_size / 2)) + (opp * h)

            if((pixel_x < 0 or pixel_y < 0) or (pixel_x > width or pixel_y > height)):
                return

            map_x = int(pixel_x / block_size)
            map_y = int(pixel_y / block_size)

            if world_map[map_y][map_x]: # inverted coordinates
                if (((int(pixel_x) % block_size) == 0) or ((int(pixel_x) % block_size) == 31)):
                    img_col = int(pixel_y) - (block[0] * block_size) # vertically
                elif (((int(pixel_y) % block_size) == 0) or ((int(pixel_y) % block_size) == 31)):
                    img_col = int(pixel_x) - (block[1] * block_size) # horizontally
                
                render(col, pixel_x, pixel_y, img_col)

                return
    

        #    draw_block(int(pixel_x), int(pixel_y), 1, (255, 255, 255, 255))

def raycast(player_angle, fov):
    col = 0
    for angle in numpy.arange(player_angle - (fov / 2), (fov / 2) + player_angle, (fov / 512)):
        single_raycast(col, angle)
        col += 1

def render(col, pixel_x, pixel_y, img_col = 0):
    global player_y

    distance_to_the_slice = math.sqrt(math.pow((player_x - pixel_x), 2) + math.pow((player_y - pixel_y), 2))
    projected_slice_height = (block_size / distance_to_the_slice) * distance_to_projection_plane
    start_pos = (height / 2) - (projected_slice_height / 2)

    for i in range(int(start_pos)):
        draw_block(col, i, 1, (63, 23, 23, 255))

    for i in range(0, int(projected_slice_height)):
        # to be fixed
        #resized_col = numpy.resize(x[:, img_col], (int(projected_slice_height), 4))

        #draw_block(col, int(start_pos) + i, 1, resized_col[i])
        draw_block(col, int(start_pos) + i, 1, (0, 255, 0, 255))

    for i in range(int(start_pos) + int(projected_slice_height), height):
        draw_block(col, i, 1, (149, 6, 6, 255))



def main():
    #frame_buffer.set_first_pixel_destination('tl')
    #rendered_img.set_first_pixel_destination('tl')

    #draw_blocks(frame_buffer)
    #draw_block(player_x, player_y, player_size, (255, 0, 0, 255), frame_buffer)

    # frame_buffer.save("frame_buffer")
    

    global player_y
    
    pygame.init()
    display = (width, height)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluOrtho2D(0, width, height, 0) 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_y += 10
                
                if event.key == pygame.K_DOWN:
                    player_y -= 10
        
        glClear(GL_COLOR_BUFFER_BIT)

        raycast(player_a, fov) 
        
        pygame.display.flip()
        pygame.time.wait(10)
    

main()