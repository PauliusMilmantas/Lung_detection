import os

masks = os.listdir(r'D:\Kursinis\Duomenys\dataset2\Annotations\masks')
xmls = os.listdir(r'D:\Kursinis\Duomenys\dataset2\Annotations\xmls')
images = os.listdir(r'D:\Kursinis\Duomenys\dataset2\JPEGImages')

for image in images:
    filename = image[:image.find(".jpg")]+'.png'
    
    if filename not in masks:
        print(image + " doesn't have a mask")
        
        os.remove(r'C:\Users\Paulius\Desktop\Duomenys\dataset2\JPEGImages\\' + image)