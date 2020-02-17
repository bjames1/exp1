import numpy as np
import glob, cv2
from PIL import Image

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

ims = imNames();

try:
    for path in ims:
        # print(im)
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        #make mask of where the transparent bits are
        trans_mask = image[:,:,3] == 0

        #replace areas of transparency with green pixels
        image[trans_mask] = [0, 255, 0, 0]

        #new image without alpha channel...
        new_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR);
        path = path.replace('.png', '.jpg');
        path = path.replace('./ims/', './ims/gb/');
        cv2.imwrite(path,new_img)

except:
    print('done') 
