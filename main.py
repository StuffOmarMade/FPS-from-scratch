import pyTGA
import math
import numpy

width = 512
height = 512
block_size = 32

player_x = 64
player_y = 40
player_size = 8

player_a = 30
fov = 90

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

def init_image(width, height):
    data = [[(0, 0, 0, 255)] * width ] * height
    image = pyTGA.Image(data)

    return image

frame_buffer = init_image(width, height)

def color_background():
    for i in range(width):
        for j in range(height):
            frame_buffer.set_pixel(j, i, (int((255 * j / height)), int((255 * i / height)), 0, 255))

def draw_block(x, y, size, color):
    for i in range(size):
        for j in range(size):
            frame_buffer.set_pixel(j + y, i + x, color)


def draw_blocks():
    for block in block_list:
        for i in range(block_size):
            for j in range(block_size):
                frame_buffer.set_pixel(j + (block_size * block[0]), i + (block_size * block[1]), (255, 255, 255, 0))

def single_raycast(angle):
        angle_in_rad = math.radians(angle)

        adj = math.cos(angle_in_rad)
        opp = math.sin(angle_in_rad)

        for h in numpy.arange(0, height - player_a, 1):
            pixel_x = (player_x + (player_size / 2)) + (adj * h)
            pixel_y = (player_y + (player_size / 2)) + (opp * h)

            if((pixel_x < 0 or pixel_y < 0) or (pixel_x > width or pixel_y > height)):
                return

            map_x = int(pixel_x / block_size)
            map_y = int(pixel_y / block_size)

            for block in block_list:
                if [map_y, map_x] == block: # inverted coordinates
                    return

            draw_block(int(pixel_x), int(pixel_y), 1, (255, 255, 255, 255))

def raycast(fov):
    for angle in range(player_a, fov + player_a):
        single_raycast(angle)

def main():
    frame_buffer.set_first_pixel_destination('tl')

    color_background()
    draw_blocks()

    draw_block(player_x, player_y, player_size, (255, 0, 0, 255))

    raycast(fov)

    frame_buffer.save("frame_buffer")

main()