import numpy as np
import cv2
from PIL import Image
import glob

def imNames():
    try:
        globTaskList = [];
        path = './ims/';
        for filename in glob.glob(path + '/*.png'):
            globTaskList.append(filename)
        globTaskList.sort()
        return globTaskList
    except:
        print('done')


# Load an color image in grayscale
path='maskTest.jpg';

image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

#make mask of where the transparent bits are
trans_mask = image[:,:,3] == 0

#replace areas of transparency with green pixels
image[trans_mask] = [0, 255, 0, 0]

#new image without alpha channel...
new_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
fileName = '_gb.jpg'
cv2.imwrite(fileName,new_img)
