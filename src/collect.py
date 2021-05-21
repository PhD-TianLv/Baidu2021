#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
注意事项：
    1. 揭下摄像头盖子
    2. 固定摄像头位置
    3. 保存数据（result.json），数据保存完成时蜂鸣器会响
"""
from joystick import JoyStick
from cart import Cart
from camera import Camera
from threading import Thread, Lock
import settings
import json
import os
from widgets import Buzzer
import cv2


class Logger:

    def __init__(self):
        self.front_camera = Camera(src=0)
        self.side_camera = Camera(src=1)
        self.started = False
        self.counter = 0
        self.map = {}
        self.resultDir = settings.resultDir
        self.sideResultDir = os.path.join(self.resultDir, 'side_cam')

        if not os.path.exists(self.resultDir):
            os.makedirs(self.resultDir)
        if settings.recordSideCam and not os.path.exists(self.sideResultDir):
            os.makedirs(self.sideResultDir)

    def start(self):
        self.started = True

    def pause(self):
        self.started = False

    def saveData(self, buzzer):
        path = os.path.join(self.resultDir, 'result.json')
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        buzzer.rings()

    def log(self):
        if self.started:
            if self.counter % 200 == 0:
                print('logging, count = {}'.format(self.counter))

            # 记录前向摄像头的数据
            front_image = self.front_camera.read()
            path = os.path.join(self.resultDir, '{}.jpg'.format(self.counter))
            cv2.imwrite(path, front_image)

            # 如果打开了侧面摄像头记录标识，则记录侧面摄像头的数据
            if settings.recordSideCam:
                side_image = self.side_camera.read()
                side_path = os.path.join(self.sideResultDir, '{}.jpg'.format(self.counter))
                cv2.imwrite(side_path, side_image)

            self.map[self.counter] = round(cart.angle, 4)  # 将记录 axis 改为记录 cart.angle 并归一化

            self.counter = self.counter + 1


def JsThread(js, cart, logger, buzzer):
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
                buzzer.rings()
                logger.pause()
                print('Key[B] down, buzzer rings, log paused, car stopped')

            # Key = A | log started
            elif number == 0 and value == 1:
                buzzer.rings()
                logger.start()
                cart.speed = cart.angle = 0
                print('Key[A] down, buzzer rings, log started, car stays still')
                cart.steer(cart.speed, cart.angle)

            # Key = Y | angle = 0
            elif number == 4 and value == 1:
                print('Key[Y] down, save data, buzzer rings')
                logger.saveData(buzzer)

        elif type_ == 2:
            # Axis | 摇杆用来微调
            if number == 0:
                value /= 32767
                cart.angle = value * cart.changeInAngle / 2  # angle: (-0.2, 0.2)
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
    buzzer = Buzzer()

    cart.velocity = settings.velocity

    js_thread = Thread(target=JsThread, args=(js, cart, logger, buzzer))
    js_thread.start()

    # 蜂鸣器响一声，作为启动的标识
    buzzer.rings()
    if settings.recordSideCam:
        print('recordSideCam open')
    print('Init complete, wait for instruction')

    while True:
        # 主进程进行数据收集工作
        logger.log()
