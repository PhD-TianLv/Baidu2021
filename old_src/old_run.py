#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import cv2
import config
from widgets import Button
from camera import Camera
from cruiser import Cruiser
from oldcart import Cart
from config import front_cam
from driver import Driver

front_camera = Camera(front_cam, [640, 480])
# side_camera = Camera(side_cam, [640, 480])
driver = Driver()
cruiser = Cruiser()
#程序开启运行开关
start_button = Button(1, "UP")
#程序关闭开关
stop_button = Button(1, "DOWN")


#确认"DOWN"按键是否按下，程序是否处于等待直行状态
def check_stop():
    if stop_button.clicked():
        return True
    return False

if __name__ == '__main__':
    front_camera.start()
    #基准速度
    driver.set_speed(25)
    #转弯系数
    driver.cart.Kx = 0.9
    #延时
    time.sleep(0.5)
    while True:
        if start_button.clicked():
            time.sleep(0.3)
            break
        print("Wait for start!")
    while True:
        front_image = front_camera.read()
        driver.go(front_image)
        if check_stop():
            driver.stop()
            print("End of program!")
            break
'''

if __name__ == '__main__':
    front_camera.start()
    #基准速度
    driver.set_speed(25)
    #转弯系数
    driver.cart.Kx = 0.9
    #延时
    time.sleep(0.5)
    while True:
        front_image = front_camera.read()
        driver.go(front_image)

