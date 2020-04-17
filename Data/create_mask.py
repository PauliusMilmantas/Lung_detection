import os
import json
import tkinter as tk
from PIL import Image, ImageDraw
from shutil import copyfile

# Constants
white = (255, 255, 255)
black = (0, 0, 0)

# Fixed object center positions
fixed_center_position = dict()

# Reading fixed object center positions from data file
data = open('center_coordinates.data', 'r')
for cnt, line in enumerate(data):
    splt = line.split(';')
    data_dict = dict()

    if splt[1] != "#":
        data_counter = 0
        for element in splt:
            if data_counter != 0:
                data_dict[str(data_counter-1)] = element
            
            data_counter += 1

        fixed_center_position[splt[0]] = data_dict
data.close()

# Path to all batches
batchpath = 'Batches/'

# Because all drawn lines are not just solid white
white_color = []
for i in range(80):
    white_color.append((255-i, 255-i, 255-i))

black_color = []
for i in range(80):
    black_color.append((i, i, i))

root = tk.Tk()
root.title("drawing lines")

batches = os.listdir(batchpath)
for batch in batches:
    with open(batchpath + batch + '/labels.json') as file:
        data = json.load(file)

        # For each file in JSON file
        for key in data.keys():
            print("Analysing: " + key)

            filename = data[key]['filename']
            regions = data[key]['regions']

            # Analysing jpg file and creating mask
            im = Image.open(batchpath + batch + '/images/' + filename)
            width, height = im.size

            # create the drawing canvas
            cv = tk.Canvas(root, width=width, height=height, bg='black')
            cv.pack()

            # create empty PIL image and draw objects to draw on
            image = Image.new("RGB", (width, height), black)
            draw = ImageDraw.Draw(image)

            object_center_coordinates = dict()

            # For each object in file we draw white lines
            for objects in regions.keys():
                # Collecting data, so that we could mark center of each object
                x_sum = 0
                y_sum = 0

                x_pos = regions[objects]['shape_attributes']['all_points_x']
                y_pos = regions[objects]['shape_attributes']['all_points_y']

                for index in range(len(x_pos)):
                    x = x_pos[index]
                    y = y_pos[index]

                    # For collecting data
                    x_sum += x
                    y_sum += y

                    # If it's first coordinates, skip them
                    if index != 0:
                        # Draw line
                        cv.create_line(x, y, last_x, last_y)
                        draw.line((x, y, last_x, last_y), white)    

                    last_x = x
                    last_y = y

                    index += 1

                # Getting center of the object
                object_center_coordinates[objects] = (int(x_sum/index), int(y_sum/index))

            # Converting jpg to png
            filename = filename.replace('jpg', 'png')

            # Exporting created mask to jpg file
            image.save('tmp/' + filename)

            # Modifying mask file with filling in holes
            im = Image.open('tmp/' + filename)
            width, height = im.size
            pixels = im.load()

            # Starting from center of each object
            objId = 0
            for obj in object_center_coordinates.keys():
                if filename in fixed_center_position.keys():
                    tmp = fixed_center_position[filename]
                    tmp = tmp[obj]

                    center_pixel_pos = (int(tmp.split(',')[0].replace('(', '')), int(tmp.split(',')[1].replace(')', '')))
                else:
                    center_pixel_pos = object_center_coordinates[obj]

                # We go to the left border, till we reach white pixel
                index = 0
                while(pixels[center_pixel_pos[0]-index, center_pixel_pos[1]] not in white_color):
                    index += 1

                index -= 1
                curr_x = center_pixel_pos[0]-index
                curr_y = center_pixel_pos[1]
                pixels[curr_x, curr_y] = (255, 255, 255)

                done = False
                memory = []
                
                # If try fails, that means that the center coordinate is wrong
                try:
                # Follow the border clock-wise and fill white color in
                    while done == False:
                        #Checking top
                        if(pixels[curr_x, curr_y-1] not in white_color):
                            pixels[curr_x, curr_y-1] = (255, 255, 255)

                            curr_y -= 1
                            memory.append((0, 1))

                        # Checking right
                        elif(pixels[curr_x+1, curr_y] not in white_color):
                            pixels[curr_x+1, curr_y] = (255, 255, 255)

                            curr_x += 1
                            memory.append((-1, 0))

                        # Checking bottom
                        elif(pixels[curr_x, curr_y+1] not in white_color):
                            pixels[curr_x, curr_y+1] = (255, 255, 255)

                            curr_y += 1
                            memory.append((0, -1))

                        # Checking left
                        elif(pixels[curr_x-1, curr_y] not in white_color):
                            pixels[curr_x-1, curr_y] = (255, 255, 255)

                            curr_x -= 1
                            memory.append((1, 0))

                        else:
                            if(len(memory) > 0):
                                step = memory.pop()
                                
                                curr_x += step[0]
                                curr_y += step[1]
                            else:
                                done = True
                # Write to center_coordinates.data, that we need new coordinates
                except:
                    print("Wrong coordinates, fix them in center_coordinates.data file  or run generate_config_file.py file!")

                    file = open('center_coordinates.data', 'a')
                    file.write('\n' + filename + ';#')
                    file.close()

                    # Copying file to not recognised pictures
                    copyfile('tmp/' + filename, batchpath + batch + '/masks_not_rec/' + filename)

            im.save(batchpath + batch + "/masks/" + filename)