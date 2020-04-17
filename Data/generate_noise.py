import numpy as np
import random
import cv2
import os
import shutil
import xml.etree.ElementTree as ET

def sp_noise(image,prob):
    '''
    Add salt and pepper noise to image
    prob: Probability of the noise
    '''
    output = np.zeros(image.shape,np.uint8)
    thres = 1 - prob 
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            rdn = random.random()
            if rdn < prob:
                output[i][j] = 0
            elif rdn > thres:
                output[i][j] = 255
            else:
                output[i][j] = image[i][j]
    return output

batchpath = 'Batches/'

batches = os.listdir(batchpath)
index = 0
print("Which batch to modify?")
for batch in batches:
    print(str(index) + ": " + batch)
    index += 1

inp = input()

print("Selected: " + batches[int(inp)])
print("Generating images and XML files...")

insideXmlFiles = os.listdir(batchpath + batches[int(inp)] + "/masks/")
insideImages = os.listdir(batchpath + batches[int(inp)] + "/images/")

for xml in insideXmlFiles:
    xmlCon = xml[0:xml.find(".")]

    print("Opening...: " + batchpath + batches[int(inp)] + "/images/" + xmlCon + ".jpg")

    image = cv2.imread(batchpath + batches[int(inp)] + "/images/" + xmlCon + ".jpg" ,0)

    for i in range(5):
        noise_img = sp_noise(image,0.01*(i+1))
        cv2.imwrite(batchpath + batches[int(inp)] + "/images/" + xmlCon + "-modified-" + str(i+1) + ".jpg", noise_img)

        # Copying XML file
        # shutil.copy(batchpath + batches[int(inp)] + "/labels/" + xmlCon + ".xml", batchpath + batches[int(inp)] + "/labels/" + xmlCon + "-modified-" + str(i+1) + ".xml")

        # Copying mask file
        shutil.copy(batchpath + batches[int(inp)] + "/masks/" + xmlCon + ".png", batchpath + batches[int(inp)] + "/masks/" + xmlCon + "-modified-" + str(i+1) + ".png")

        # Modifying copied XML for file path
        # tree = ET.parse(batchpath + batches[int(inp)] + "/labels/" + xmlCon + "-modified-" + str(i+1) + ".xml")
        # root = tree.getroot()

        # for child in root:
        #     if(child.tag == "filename"):
        #         child.text = xmlCon + "-modified-" + str(i+1) + ".jpg"
        #     if(child.tag == "path"):
        #         child.text = "/my-project-name/" + xmlCon + "-modified-" + str(i+1) + ".jpg"

        # tree.write(batchpath + batches[int(inp)] + "/labels/" + xmlCon + "-modified-" + str(i+1) + ".xml")

    print("Generated images for: " + xmlCon + ".jpg")