#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
注意事项：
    1. 揭下摄像头盖子
    2. 固定摄像头位置
    3. 保存数据，数据保存完成时蜂鸣器会响
"""
from joystick import JoyStick
from cart import Cart
from camera import Camera
from threading import Thread, Lock
from widgets import Buzzer
import settings
import json
import os
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

    def pause(self):
        self.started = False

    def saveData(self):
        path = os.path.join(self.resultDir, 'result.json')
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        self.buzzer.rings()

    def log(self):
        if self.started:
            if self.counter % 200 == 0:
                print('logging, count = {}'.format(self.counter))
            image = self.camera.read()
            path = os.path.join(self.resultDir, '{}.jpg'.format(self.counter))

            # 将记录 axis 改为记录 cart.angle 并归一化
            self.map[self.counter] = round(cart.angle, 4)
            cv2.imwrite(path, image)
            self.counter = self.counter + 1


def JsThread(js, cart, logger):
    while True:
        time, value, type_, number = js.read()

        if type_ == 1:
            # Key = X | log started | angle = 0
            if number == 3 and value == 1:
                cart.speed = cart.velocity
                cart.angle = 0
                logger.start()
                print('Key[X] down, log started, run at {}, angle = {:.1f}'.format(cart.speed, cart.angle))
                cart.steer(cart.speed, cart.angle)

            # Key = B | cart stopped | log paused | keep the value of angle
            elif number == 1 and value == 1:
                cart.speed = cart.angle = 0
                cart.steer(cart.speed, cart.angle)
                logger.pause()
                print('Key[B] down, log paused, car stopped')

            # Key = Y | angle = 0
            elif number == 4 and value == 1:
                print('Key[Y] down, save_data')
                logger.saveData()

        elif type_ == 2:
            # Axis | 摇杆用来微调
            if number == 0:
                value /= 32767
                cart.angle = value * cart.changeInAngle  # angle: (-0.2, 0.2)
                cart.steer(cart.speed, cart.angle)
                print('Axis down, angle = {:.4f}'.format(cart.angle))

            # Key = LEFT | angle -= cart.angle_changeValue
            elif number == 6 and value == -32767:
                if logger.started:
                    if cart.angle == cart.minAngle:
                        print('Key[LEFT] down, angle == {:.1f}, maximizing'.format(cart.minAngle))
                    else:
                        cart.angle -= cart.changeInAngle
                        print('Key[LEFT] down, angle -= {:.1f}, now angle = {:.1f}'.format(cart.changeInAngle,
                                                                                           cart.angle))
                    cart.speed = cart.velocity + abs(cart.angle) * (cart.maxSpeed - cart.velocity) / 4
                    cart.steer(cart.speed, cart.angle)

            # Key = RIGHT | angle += cart.angle_changeValue
            elif number == 6 and value == 32767:
                if logger.started:
                    if cart.angle == cart.maxAngle:
                        print('Key[RIGHT] down, angle == {:.1f}, maximizing'.format(cart.maxAngle))
                    else:
                        cart.angle += cart.changeInAngle
                        print('Key[RIGHT] down, angle += {:.1f}, now angle = {:.1f}'.format(cart.changeInAngle,
                                                                                            cart.angle))
                    cart.speed = cart.velocity + abs(cart.angle) * (cart.maxSpeed - cart.velocity) / 4
                    cart.steer(cart.speed, cart.angle)


if __name__ == "__main__":
    settings.set_working_dir()

    log_lock = Lock()
    js = JoyStick()
    cart = Cart()
    logger = Logger()

    # param set
    # cart.velocity = 100 # DEBUG
    cart.velocity = settings.velocity

    js_thread = Thread(target=JsThread, args=(js, cart, logger))
    js_thread.start()
    print('Init complete, wait for instruction')

    # 作为启动的标识
    cart.move([10, 10, 10, 10])
    cart.move([0, 0, 0, 0])

    while True:
        logger.log()
