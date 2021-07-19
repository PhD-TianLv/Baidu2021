# 定义数据增强手段
import cv2
import random
from PIL import Image, ImageEnhance
import numpy as np
import os
from matplotlib import pyplot as plt


# 随机改变亮暗、对比度和颜色等
def random_distort(img):
    # 随机改变亮度
    def random_brightness(img, lower=0.8, upper=1.2):
        e = np.random.uniform(lower, upper)
        return ImageEnhance.Brightness(img).enhance(e)

    # 随机改变对比度
    def random_contrast(img, lower=0.5, upper=1.5):
        e = np.random.uniform(lower, upper)
        return ImageEnhance.Contrast(img).enhance(e)

    # 随机改变颜色
    def random_color(img, lower=0.5, upper=1.5):
        e = np.random.uniform(lower, upper)
        return ImageEnhance.Color(img).enhance(e)

    ops = [random_brightness, random_contrast, random_color]
    np.random.shuffle(ops)

    img = Image.fromarray(img)
    img = ops[0](img)
    # img = ops[1](img)
    # img = ops[2](img)
    img = np.asarray(img)

    return img


def random_brightness(img, lower=0.5, upper=1.5):
    e = np.random.uniform(lower, upper)
    return ImageEnhance.Brightness(img).enhance(e)


if __name__ == '__main__':
    os.chdir('D:/WorkSpace/Baidu2021/')
    img = cv2.imread('data/train11/0.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = random_distort(img)

    plt.imshow(img)
    plt.show()
