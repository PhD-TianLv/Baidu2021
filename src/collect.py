#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
"""

from joystick import JoyStick
from cart import Cart
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
        # 暂停，同时保存 angle 数据文件
        self.started = False
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)

    def stop(self):
        if self.stopped_:
            return
        self.stopped_ = True
        cart.stop()
        path = "{}/result.json".format(self.result_dir)
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)

    def log(self):
        if self.started:
            return_value, image = self.camera.read()
            path = "{}/{}.jpg".format(self.result_dir, self.counter)
            # 将记录 axis 改为记录 cart.angle 并归一化
            self.map[self.counter] = cart.angle / 4
            cv2.imwrite(path, image)
            if self.counter % 100 == 0:
                print('logging, count = {}'.format(self.counter))
            self.counter = self.counter + 1

    def stopped(self):
        return self.stopped_


def JsRunThread(js, cart, logger):
    while True:
        cart.steer(cart.speed, cart.angle)

        time, value, type_, number = js.read()
        # Key = X | log started | angle = 0
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = cart.velocity
            cart.angle = 0
            logger.start()
            print('Key[X] down, log started, run at {}, angle = {:.1f}'.format(cart.speed, cart.angle))

        # Key = B | cart stopped | log paused | keep the value of angle
        if type_ == 1 and number == 1 and value == 1:
            cart.speed = 0
            logger.pause()
            print('Key[B] down, log paused, car stopped')

        # Key = Y | angle = 0
        # if type_ == 1 and number == 4 and value == 1:
        #     cart.angle = 0
        #     print('Key[Y] down, angle = 0')

        # Key = LEFT | angle -= cart.angle_changeValue
        if type_ == 2 and number == 6 and value == -32767:
            if cart.angle == cart.min_angle:
                print('Key[LEFT] down, angle == {:.1f}, maximizing'.format(cart.min_angle))
            else:
                cart.angle -= cart.angle_changeValue
                print('Key[LEFT] down, angle -= {:.1f}, now angle = {:.1f}'.format(cart.angle_changeValue, cart.angle))

        # Key = RIGHT | angle += cart.angle_changeValue
        if type_ == 2 and number == 6 and value == 32767:
            if cart.angle == cart.max_angle:
                print('Key[RIGHT] down, angle == {:.1f}, maximizing'.format(cart.max_angle))
            else:
                cart.angle += cart.angle_changeValue
                print('Key[RIGHT] down, angle += {:.1f}, now angle = {:.1f}'.format(cart.angle_changeValue, cart.angle))


if __name__ == "__main__":
    js = JoyStick()
    js.open()
    logger = Logger()
    cart = Cart()

    # param
    cart.velocity = 50

    js_run_thread = threading.Thread(target=JsRunThread, args=(js, cart, logger))
    js_run_thread.start()
    print('Init complete, wait for instruction')

    while True:
        logger.log()

    js_run_thread.join()
    cart.stop()
