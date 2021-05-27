import os
import shutil
import re
import cv2 as cv
import numpy as np

os.chdir('/')


def img_extract(img_path, save_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    img_name = os.listdir(img_path)
    img_name.remove('result.json')
    lower_hsv = np.array([20, 75, 165])
    upper_hsv = np.array([40, 255, 255])

    for img in img_name:
        image = os.path.join(img_path, img)
        src = cv.imread(image)
        hsv = cv.cvtColor(src, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
        ind = int(re.findall('.+(?=.jpg)', img)[0])
        new_name = str(ind) + '.jpg'
        cv.imwrite(os.path.join(save_path, new_name), mask)

    shutil.copy(os.path.join(img_path, 'result.json'), save_path)


if __name__ == '__main__':
    img_path = 'data/train4'
    save_path = 'data/train4_hsv'
    img_extract(img_path, save_path)
    print('img_extract finished!')
