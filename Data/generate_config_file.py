import os
import json
import tkinter as tk
from PIL import Image, ImageDraw

def is_black(color_range, pixel_rgb):    
    return pixel_rgb[0] < 50 and pixel_rgb[1] < 50 and pixel_rgb[2] < 50

def is_white(color_range, pixel_rgb):
    return pixel_rgb[0] > 200 and pixel_rgb[1] > 200 and pixel_rgb[2] > 200

# Constants
color_range = 50

# Path to all batches
batchpath = 'Batches/'

# Config file
data = open('center_coordinates.data', 'a')

batches = os.listdir(batchpath)
for batch in batches:
    # Reading all 'masks_not_rec' folders
    images = os.listdir(batchpath + batch + '/masks_not_rec/')

    for img in images:
        # Loading image
        im = Image.open(batchpath + batch + '/masks_not_rec/' + img)
        width, height = im.size
        pixels = im.load()

        detected_pixels = []
        for x_coord in range(width):
            for y_coord in range(height):
                if is_black(color_range, pixels[x_coord, y_coord]) == False and is_white(color_range, pixels[x_coord, y_coord]) == False:
                    detected_pixels.append('(' + str(x_coord) + ', ' + str(y_coord) + ')')
                    print(img + " " + str(pixels[x_coord, y_coord]) + ' x: ' + str(x_coord) + ' y: ' + str(y_coord))
        
        data.write('\n' + img)
        for d_pixel in detected_pixels:
             data.write(';' + d_pixel)

data.close()