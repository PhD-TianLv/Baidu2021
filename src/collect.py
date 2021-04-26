#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
"""

from joystick import JoyStick
from cart import Cart
import time
import cv2
from threading import Thread, Lock
import json
import config
import os


class Logger:

    def __init__(self):
        self.camera = cv2.VideoCapture(config.front_cam)
        self.started = False
        self.counter = 0
        self.map = {}
        self.result_dir = "../train/"
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)

    def start(self, lock):
        lock.acquire()
        self.started = True
        lock.release()

    def pause(self, lock):
        # 暂停，同时保存 angle 数据文件
        path = os.path.join(self.result_dir, 'result.json')

        lock.acquire()
        self.started = False
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        lock.release()

    def stop(self, lock):
        path = os.path.join(self.result_dir, 'result.json')

        lock.acquire()
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        lock.release()

    def log(self, lock):
        if self.counter % 100 == 0:
            print('logging, count = {}'.format(self.counter))
        return_value, image = self.camera.read()
        path = os.path.join(self.result_dir, '{}.jpg'.format(self.counter))

        lock.acquire()
        # 将记录 axis 改为记录 cart.angle 并归一化
        self.map[self.counter] = cart.angle / 4
        cv2.imwrite(path, image)
        self.counter = self.counter + 1
        lock.release()


def JsRunThread(run_flag, js, cart, logger):
    while run_flag:
        # Run
        cart.steer(cart.speed, cart.angle)

        # JoystickContorl
        time, value, type_, number = js.read()
        # Key = X | log started | angle = 0
        if 'X' in js.get_key():
            cart.speed = cart.velocity
            cart.angle = 0
            logger.start()
            print('Key[X] down, log started, run at {}, angle = {:.1f}'.format(cart.speed, cart.angle))

        # Key = B | cart stopped | log paused | keep the value of angle
        if 'B' in js.get_key():
            cart.speed = 0
            logger.pause()
            print('Key[B] down, log paused, car stopped')

        # Key = Y | angle = 0
        # if type_ == 1 and number == 4 and value == 1:
        #     cart.angle = 0
        #     print('Key[Y] down, angle = 0')

        # Key = LEFT | angle -= cart.angle_changeValue
        if 'LEFT' in js.get_key():
            if cart.angle == cart.min_angle:
                print('Key[LEFT] down, angle == {:.1f}, maximizing'.format(cart.min_angle))
            else:
                cart.angle -= cart.change_in_angle
                print('Key[LEFT] down, angle -= {:.1f}, now angle = {:.1f}'.format(cart.change_in_angle, cart.angle))

        # Key = RIGHT | angle += cart.angle_changeValue
        if 'RIGHT' in js.get_key():
            if cart.angle == cart.max_angle:
                print('Key[RIGHT] down, angle == {:.1f}, maximizing'.format(cart.max_angle))
            else:
                cart.angle += cart.change_in_angle
                print('Key[RIGHT] down, angle += {:.1f}, now angle = {:.1f}'.format(cart.change_in_angle, cart.angle))


def LogThread(run_flag, logger, lock):
    while run_flag:
        if logger.started:
            logger.log(lock)


if __name__ == "__main__":
    js = JoyStick()
    logger = Logger()
    cart = Cart()
    lock = Lock()
    run_flag = True

    # param set
    cart.velocity = 50

    js_run_thread = Thread(target=JsRunThread, args=(run_flag, js, cart, logger))
    log_thread = Thread(target=LogThread, args=(run_flag, logger, lock))
    js_run_thread.start()
    log_thread.start()
    print('Init complete, wait for instruction')

    while True:
        pass

    # end of program
    run_flag = False
    js_run_thread.join()
    log_thread.join()
    logger.stop()
    cart.stop()
