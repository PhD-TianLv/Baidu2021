#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
本文件用作无人驾驶车道数据采集
注意事项：揭下摄像头盖子
"""
from joystick import JoyStick
from cart import Cart
from camera import Camera
from threading import Thread, Lock
from widgets import Buzzer
import settings
import json
import os
import shutil
import cv2


class Logger:

    def __init__(self):
        self.camera = Camera()
        self.started = False
        self.counter = 0
        self.map = {}
        self.buzzer = Buzzer()
        self.resultDir = settings.resultDir
        self.emptyDataStr = ""

        self.processFolder()

    def processFolder(self):
        if os.path.exists(self.resultDir) and os.path.getsize(self.resultDir) > 1024 * 1024:
            shutil.rmtree(self.resultDir)
        if not os.path.exists(self.resultDir):
            os.makedirs(self.resultDir)

    def emptyData(self, pq_lock, log_lock):
        pq_lock.acquire()

        # 删除数据
        log_lock.acquire()
        if os.path.exists(self.resultDir):
            shutil.rmtree(self.resultDir)
        if not os.path.exists(self.resultDir):
            os.makedirs(self.resultDir)
        log_lock.release()

        # 重置数据记录状态
        self.counter = 0
        self.map = {}

        # 数据删除完成，蜂鸣器响
        self.buzzer.rings()

        pq_lock.release()

    def start(self):
        self.started = True

    def pause(self):
        # 暂停，同时保存 angle 数据文件
        self.started = False

    def saveData(self, log_lock):
        log_lock.acquire()
        path = os.path.join(self.resultDir, 'result.json')
        with open(path, 'w') as fp:
            json.dump(self.map.copy(), fp)
        log_lock.release()

    def log(self, lock):
        if self.counter % 200 == 0:
            print('logging, count = {}'.format(self.counter))
        image = self.camera.read()
        path = os.path.join(self.resultDir, '{}.jpg'.format(self.counter))

        # 需要判断 logger.started 是否为 True ，因此在前设置 lock
        lock.acquire()
        if self.started:
            # 将记录 axis 改为记录 cart.angle 并归一化
            self.map[self.counter] = int(int(cart.angle * 10000) / 10000)
            cv2.imwrite(path, image)
            self.counter = self.counter + 1
        lock.release()


def RecordKey(value, type_, number, pq_lock, log_lock, logger, cart):
    # 记录按键
    # Key = A
    if type_ == 1 and number == 0 and value == 1:
        logger.emptyDataStr += 'A'
        # print('Key[A] down, logger.emptyDataStr += A')

    # Key = B | cart stopped | log paused | keep the value of angle
    elif type_ == 1 and number == 1 and value == 1:
        logger.emptyDataStr += 'B'
        # print('Key[B] down, logger.emptyDataStr += B')

    # Key = LEFT
    elif type_ == 2 and number == 6 and value == -32767:
        logger.emptyDataStr += '←'
        # print('Key[LEFT] down, logger.emptyDataStr += ←')

    # Key = RIGHT
    elif type_ == 2 and number == 6 and value == 32767:
        logger.emptyDataStr += '→'
        # print('Key[RIGHT] down, logger.emptyDataStr += →')

    # Key = UP
    elif type_ == 2 and number == 7 and value == -32767:
        logger.emptyDataStr += '↑'
        # print('Key[UP] down, logger.emptyDataStr += ↑')

    # Key = Down
    elif type_ == 2 and number == 7 and value == 32767:
        logger.emptyDataStr += '↓'
        # print('Key[DOWN] down, logger.emptyDataStr += ↓')

    elif type_ in [1, 2] and not value == 0:
        logger.emptyDataStr = ""
        # print('others key down, logger.emptyDataStr.clear()')

    # 触发[数据清空]操作
    if logger.emptyDataStr.endswith('↑↑↓↓←→←→ABAB'):
        logger.emptyDataStr = ""

        cart.stop()
        logger.pause()
        print('operation data clearance has been triggered to clear data')
        Thread(target=logger.emptyData, args=(pq_lock, log_lock)).start()

    if len(logger.emptyDataStr) > 40:
        logger.emptyDataStr = logger.emptyDataStr[20:]


def JsThread(run_flag, pq_lock, log_lock, js, cart, logger):
    while run_flag:
        # 数据处理为最高优先级：处理数据时，不接收手柄信息
        if pq_lock.locked():
            cart.move([0, 0, 0, 0])
            continue

        time, value, type_, number = js.read()
        # print('type_ = {}, number = {}, value = {}'.format(type_, number, value))  # DEBUG
        Thread(target=RecordKey, args=(value, type_, number, pq_lock, log_lock, logger, cart)).start()

        # Key = X | log started | angle = 0
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = cart.velocity
            cart.angle = 0
            logger.started = True
            print('Key[X] down, log started, run at {}, angle = {:.1f}'.format(cart.speed, cart.angle))
            cart.steer(cart.speed, cart.angle)

        # Key = B | cart stopped | log paused | keep the value of angle
        elif type_ == 1 and number == 1 and value == 1:
            cart.move([0, 0, 0, 0])  # 优先停止
            cart.speed = 0
            logger.started = False
            print('Key[B] down, log paused, car stopped')
            Thread(target=logger.saveData, args=(log_lock,)).start()

        # Key = Y | angle = 0
        # if type_ == 1 and number == 4 and value == 1:
        #     cart.angle = 0
        #     print('Key[Y] down, angle = 0')

        # Axis
        elif type_ == 2 and number == 0:
            value /= 32767
            cart.speed = cart.velocity + abs(value) * (cart.maxSpeed - cart.velocity) / 4
            cart.angle = value  # angle: (-1, 1)
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


def LogThread(run_flag, pq_lock, log_lock, logger):
    while run_flag:
        if not logger.started or pq_lock.locked():
            continue
        logger.log(log_lock)


if __name__ == "__main__":
    settings.set_working_dir(__file__)

    log_lock = Lock()
    pq_lock = Lock()
    js = JoyStick()
    cart = Cart()
    logger = Logger()
    run_flag = True

    # param set
    # cart.velocity = 100 # DEBUG
    cart.velocity = settings.velocity

    js_thread = Thread(target=JsThread, args=(run_flag, pq_lock, log_lock, js, cart, logger))
    log_thread = Thread(target=LogThread, args=(run_flag, pq_lock, log_lock, logger))
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
