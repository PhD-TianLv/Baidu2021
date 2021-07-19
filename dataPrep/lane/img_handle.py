import os
import shutil
import re
import cv2 as cv
import numpy as np
from preprocessing import *

os.chdir('D:/WorkSpace/Baidu2021/')


def img_extract(img_path, save_path):
    # enhance_path = 'data/train11_enhance'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # if not os.path.exists(enhance_path):
    #     os.makedirs(enhance_path)

    img_name = os.listdir(img_path)
    img_name.remove('result.json')
    lower_hsv = np.array([20, 75, 165])
    upper_hsv = np.array([40, 255, 255])

    for index, img in enumerate(img_name):
        image = os.path.join(img_path, img)
        src = cv.imread(image)

        # 数据增强, 只加上了亮度
        enhance = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
        enhance = random_distort(enhance)
        enhance = cv2.cvtColor(enhance, cv2.COLOR_RGB2BGR)

        hsv = cv.cvtColor(enhance, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
        ind = int(re.findall('.+(?=.jpg)', img)[0])
        new_name = str(ind) + '.jpg'
        # cv.imwrite(os.path.join(enhance_path, new_name), enhance)
        cv.imwrite(os.path.join(save_path, new_name), mask)
        if index % 1000 == 0:
            print('complete index = {}'.format(index))

    shutil.copy(os.path.join(img_path, 'result.json'), save_path)


if __name__ == '__main__':
    img_path = 'data/train11'
    save_path = 'data/train11_hsv'
    img_extract(img_path, save_path)
    print('img_extract finished!')
