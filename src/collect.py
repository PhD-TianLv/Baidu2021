#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
"""

from joystick import JoyStick
from old_cart import Cart
import time
import cv2
import threading
import json
import config


class Logger:

    def __init__(self):
        self.camera = cv2.VideoCapture(config.front_cam)
        self.started = False
        self.stopped_ = False
        self.counter = 0
        self.map = {}
        self.result_dir = "../train"

    def start(self):
        self.started = True

    def pause(self):
        self.started = False

    def stop(self):
        if self.stopped_:
            return
        self.stopped_ = True
        cart.stop()
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)

    def log(self, axis):
        if self.started:
            return_value, image = self.camera.read()
            path = "{}/{}.jpg".format(self.result_dir, self.counter)
            # 将记录 axis 改为记录 cart.angle 并归一化
            self.map[self.counter] = cart.angle / 4
            cv2.imwrite(path, image)
            self.counter = self.counter + 1

    def stopped(self):
        return self.stopped_


def joystick_thread(js, cart, logger):
    while True:
        time, value, type_, number = js.read()
        # Key = X | log started
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = 50  # Speed
            logger.start()
            print('Key[X] down, log started, run at {}'.format(cart.speed))

        # Key = B | cart stopped | log paused | keep the value of angle
        if type_ == 1 and number == 1 and value == 1:
            cart.speed = 0
            logger.pause()
            print('Key[B] down, log paused, car stopped')

        # Key = Y | angle = 0
        if type_ == 1 and number == 4 and value == 1:
            cart.angle = 0
            print('Key[Y] down, angle = 0')

        # Key = LEFT | angle -= 0.25
        if type_ == 2 and number == 6 and value == -32767:
            if cart.angle == cart.min_speed:
                print('Key[LEFT] down, angle == -2.0, maximizing')
            else:
                cart.angle -= 0.25
                print('Key[LEFT] down, angle -= 0.25, now angle = {}'.format(cart.angle))

        # Key = RIGHT | angle += 0.25
        if type_ == 2 and number == 6 and value == 32767:
            if cart.angle == cart.max_speed:
                print('Key[RIGHT] down, angle == 2.0, maximizing')
            else:
                cart.angle += 0.25
                print('Key[RIGHT] down, angle += 0.25, now angle = {}'.format(cart.angle))


if __name__ == "__main__":
    js = JoyStick()
    logger = Logger()
    cart = Cart()

    js_thread = threading.Thread(target=joystick_thread, args=(js, cart, logger))
    js_thread.start()
    while not logger.stopped():
        # time.sleep(0.01)
        logger.log(js.x_axis)

    js_thread.join()
    cart.stop()
