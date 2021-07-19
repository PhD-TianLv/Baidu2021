import serial
import signal
from threading import Thread

import settings


def set_timeout(num):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(num)  # 设置 num 秒的闹钟
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                print('laser flush runtime out!')

        return to_do

    return wrap


class Laser:
    def __init__(self, port):
        portx = "/dev/" + str(port)
        bps = 115200
        self.serial = serial.Serial(portx,
                                    int(bps),
                                    timeout=0.01,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1)

        try:
            self.serial.open()
        except Exception as e:
            if not str(e) == 'Port is already open.':
                raise Exception("error open serial port: " + str(e))

    def read(self):
        @set_timeout(1)
        def flushclear():
            self.serial.flushInput()
            self.serial.flushOutput()

        try:
            flushclear()
        except:
            pass

        distance = None
        while not distance:
            try:
                flushclear()
            except:
                pass

            response = self.serial.readline()
            try:
                distance = float(response.decode('utf-8'))
            except:
                distance = None
                # print('warning: laser cannot get response!')
        return distance


def test_laser():
    laser = Laser(2)
    while True:
        print(laser.read())

    from cart import Cart
    from threading import Lock

    cart = Cart()
    cart.angle = 0

    laser_left = Laser(port=2)
    laser_right = Laser(port=1)

    while True:
        # cart.steer(10, 0)
        dis_left, dis_right = float(laser_left.read()), float(laser_right.read())
        print('%.2f' % dis_left, '%.2f' % dis_right)

    lock = Lock()

    turn = ""
    while True:
        lock.acquire()
        dis_left, dis_right = float(laser_left.read()), float(laser_right.read())
        lock.release()
        if -1.0 in [dis_left, dis_right]:
            continue

        if abs(dis_left - dis_right) < 0.04:
            move = [0, 0, 0, 0]
            lock.acquire()
            cart.move(move)
            lock.release()
            turn = 'stop'
            break
        elif dis_left > dis_right:
            move = [-10, -10, -5, -5]
            turn = 'right'
        elif dis_left < dis_right:
            move = [10, 10, 5, 5]
            turn = 'left'
        lock.acquire()
        cart.move(move)
        lock.release()

        print("laser_left=%.2f,laser_right=%.2f" % (laser_left.read(), laser_right.read()) + ",turn={}".format(
            turn))


if __name__ == '__main__':
    laser1 = Laser(port=settings.laser1_port)
    laser2 = Laser(port=settings.laser2_port)
    # print(laser1.read())
    # print(laser2.read())
    while True:
        print(laser1.read(), laser2.read())
        pass
