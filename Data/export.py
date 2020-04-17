import os
import xml.etree.ElementTree as ET
import pandas as pd
import shutil

# Hashmap for image files
imageFiles = {}

# Data for writing to excel
dataframe = [] # All data
dataframetraining = [] # Data for training
dataframetesting = [] # Data for testing

# How many lines to accept for testing
dataLimitForTesting = int(input("How many test variants?: (Default 0) "))

if dataLimitForTesting == "":
    dataLimitForTesting = 0

acceptedType = dict() # For accepting each organ the same amount of times

# Reading XML files
batchpath = 'Batches/'

# For renaming files and making them unique
fileNameIndex = 0
batchNameIndex = 0

batches = os.listdir(batchpath)
for batch in batches:
    batchNameIndex += 1
    inside = os.listdir(batchpath + batch + "/")
    
    # Registering images, to check if any of then is unused
    images = os.listdir(batchpath + batch + "/images/")
    for image in images:
        imageFiles[image] = 0

    # XML data
    XMLs = os.listdir(batchpath + batch + "/labels/")
    
    for XML in XMLs:
        tree = ET.parse(batchpath + batch + "/labels/" + XML)
        root = tree.getroot()

        name = "" # class name
        folder = ""
        filename = ""
        xmin = ""
        ymin = ""
        xmax = ""
        ymax = ""
        width = ""
        height = ""

        for child in root:
            if(child.tag == "object"):
                for subchild in child:
                    if(subchild.tag == "name"):
                        name = subchild.text
                    elif(subchild.tag == "bndbox"):
                        for ss in subchild:
                            if(ss.tag == "xmin"):
                                xmin = ss.text
                            elif(ss.tag == "ymin"):
                                ymin = ss.text
                            elif(ss.tag == "xmax"):
                                xmax = ss.text
                            elif(ss.tag == "ymax"):
                                ymax = ss.text
            elif(child.tag == "path"):
                folder = child.text
            elif(child.tag == "filename"):
                filename = child.text
                imageFiles[filename] = 1
            elif(child.tag == "size"):
                for sz in child:
                    if(sz.tag == "width"):
                        width = sz.text
                    elif(sz.tag == "height"):
                        height = sz.text

        # Modyfying filename
        fileNameIndex += 1
        newFileName = filename[0:filename.find(".")] + "-" + str(batchNameIndex) + "-" + str(fileNameIndex) + ".png"

        # Copying image and XML files
        shutil.copy(batchpath + batch + "/images/" + filename, "Images/All/" + newFileName)
        shutil.copy(batchpath + batch + "/labels/" + filename.replace('.jpg', '.xml'), "Images/xmls/" + newFileName.replace('.png', '.xml'))

        # Modifying copied XML files
        local_tree = ET.parse(batchpath + batch + "/labels/" + XML)
        local_root = local_tree.getroot()

        for local_child in local_root:
            if local_child.tag == "filename":
                local_child.text = newFileName
            elif local_child.tag == "path":
                local_child.text = "C:/tenserflow1/models/research/object_detection/images/annotations/xmls/" + newFileName
            elif local_child.tag == "object":
                for local_child_1  in local_child:
                    if local_child_1.tag == "truncated":
                        local_child_1.text = "0"
                    elif local_child_1.tag == "difficult":
                        local_child_1.text = "0"

        local_tree.write('Images/xmls/' + newFileName.replace('.png', '.xml'))

        # Copying mask files
        masks = os.listdir(batchpath + batch + "/masks/")
        for mask in masks:
            shutil.copy(batchpath + batch + "/masks/" + filename.replace('.jpg', '.png'), "Images/masks/" + newFileName)

        # Data for writing to excel
        dataframe.append([newFileName, width, height, name, xmin, ymin, xmax, ymax])

        # Clasifying data for testing and training
        if name in acceptedType.keys():
            organIndex = acceptedType[name]
        else:
            organIndex = 0

        if(dataLimitForTesting < organIndex):
            # For training
            dataframetraining.append([newFileName, width, height, name, xmin, ymin, xmax, ymax])

            shutil.copy(batchpath + batch + "/images/" + filename, "Images/Training/" + newFileName)

        else:
            # For testing
            dataframetesting.append([newFileName, width, height, name, xmin, ymin, xmax, ymax])

            shutil.copy(batchpath + batch + "/images/" + filename, "Images/Testing/" + newFileName)

            if name in acceptedType.keys():
                acceptedType[name] += 1
            else:
                acceptedType[name] = 0

# Writing to excel
df1 = pd.DataFrame(dataframe,
                   columns=['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax'])
df1.to_excel("output.xlsx")  

# For clasifying: testing or training
if dataLimitForTesting > 0:
    trainingExcl = pd.DataFrame(dataframetesting,
                    columns=['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax'])
    trainingExcl.to_excel("testing.xlsx")  

    testingExcl = pd.DataFrame(dataframetraining,
                    columns=['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax'])
    testingExcl.to_excel("training.xlsx")  

print("Images copied to: Images/All, Excel created at: output.xls")