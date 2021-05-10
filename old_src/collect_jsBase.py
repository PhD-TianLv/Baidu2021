#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
注意事项：
    1. 揭下摄像头盖子
    2. 固定摄像头位置
"""
from joystick import JoyStick
from cart import Cart
from camera import Camera
from threading import Thread, Lock
import settings
import json
import os
import shutil
from widgets import Buzzer
import cv2


class Logger:

    def __init__(self):
        self.camera = Camera()
        self.started = False
        self.buzzer = Buzzer()
        self.counter = 0
        self.map = {}
        self.resultDir = settings.resultDir
        if not os.path.exists(self.resultDir):
            os.makedirs(self.resultDir)

    def start(self):
        self.started = True
        self.camera.start()

    def pause(self):
        self.started = False
        self.camera.pause()

    def saveData(self):
        path = os.path.join(self.resultDir, 'result.json')
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        self.buzzer.rings()

    def log(self):
        if self.counter % 200 == 0:
            print('logging, count = {}'.format(self.counter))
        image = self.camera.read()
        path = os.path.join(self.resultDir, '{}.jpg'.format(self.counter))

        # 将记录 axis 改为记录 cart.angle 并归一化
        self.map[self.counter] = int(int(cart.angle * 10000) / 10000)
        cv2.imwrite(path, image)
        self.counter = self.counter + 1


def JsThread(run_flag, log_lock, js, cart, logger):
    while run_flag:
        time, value, type_, number = js.read()

        # Key = X | log started | angle = 0
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = cart.velocity
            cart.angle = 0
            logger.start()
            print('Key[X] down, log started, run at {}, angle = {:.1f}'.format(cart.speed, cart.angle))
            cart.steer(cart.speed, cart.angle)

        # Key = B | cart stopped | log paused | keep the value of angle
        elif type_ == 1 and number == 1 and value == 1:
            cart.speed = cart.angle = 0
            cart.steer(cart.speed, cart.angle)
            logger.pause()
            print('Key[B] down, log paused, car stopped')

        # Key = Y | angle = 0
        elif type_ == 1 and number == 4 and value == 1:
            print('Key[Y] down, save_data')
            logger.saveData()

        # Axis | 摇杆用来微调
        elif type_ == 2 and number == 0:
            value /= 32767
            cart.angle = value / 10  # angle: (-0.1, 0.1)
            cart.steer(cart.speed, cart.angle)
            # print('Axis down, angle = {}'.format(cart.angle))

        # Key = LEFT | angle -= cart.angle_changeValue
        elif type_ == 2 and number == 6 and value == -32767:
            if cart.angle == cart.minAngle:
                print('Key[LEFT] down, angle == {:.1f}, maximizing'.format(cart.minAngle))
            else:
                cart.angle -= cart.changeInAngle
                print('Key[LEFT] down, angle -= {:.1f}, now angle = {:.1f}'.format(cart.changeInAngle, cart.angle))
            cart.steer(cart.speed, cart.angle)

        # Key = RIGHT | angle += cart.angle_changeValue
        elif type_ == 2 and number == 6 and value == 32767:
            if cart.angle == cart.maxAngle:
                print('Key[RIGHT] down, angle == {:.1f}, maximizing'.format(cart.maxAngle))
            else:
                cart.angle += cart.changeInAngle
                print('Key[RIGHT] down, angle += {:.1f}, now angle = {:.1f}'.format(cart.changeInAngle, cart.angle))
            cart.steer(cart.speed, cart.angle)


def LogThread(run_flag, log_lock, logger):
    while run_flag:
        if not logger.started:
            continue
        logger.log(log_lock)


if __name__ == "__main__":
    settings.set_working_dir(__file__)

    log_lock = Lock()
    js = JoyStick()
    cart = Cart()
    logger = Logger()
    run_flag = True

    # param set
    # cart.velocity = 100 # DEBUG
    cart.velocity = settings.velocity

    js_thread = Thread(target=JsThread, args=(run_flag, log_lock, js, cart, logger))
    log_thread = Thread(target=LogThread, args=(run_flag, log_lock, logger))
    js_thread.start()
    log_thread.start()
    print('Init complete, wait for instruction')

    # 作为启动的标识
    cart.move([10, 10, 10, 10])
    cart.move([0, 0, 0, 0])

    while True:
        pass

    # end of program
    run_flag = False
    logger.stop()
    cart.stop()
