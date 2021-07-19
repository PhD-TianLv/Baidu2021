import binascii
import signal

import serial
import time

#到场地后校准磁罗盘 以及测量赛道角度
import settings


def set_timeout(num, mode='read'):
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
                print('compass {} runtime out!'.format(mode))

        return to_do

    return wrap


class Compass:
    def __init__(self, port, init_flag=True):
        portx = "/dev/" + str(port)
        bps = 115200
        self.serial = serial.Serial(portx,
                                    int(bps),
                                    bytesize=serial.EIGHTBITS,
                                    timeout=0.001,  # 不许改动
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    xonxoff=False,
                                    rtscts=False,
                                    dsrdtr=False,
                                    writeTimeout=1)
        self.angle = -1
        self.run_flag = True

        try:
            self.serial.open()
        except Exception as e:
            if not str(e) == 'Port is already open.':
                raise Exception("error open serial port: " + str(e))

        # 初始化
        if init_flag:
            self.initialize()

    def initialize(self):
        @set_timeout(1, mode='flush')
        def flushclear():
            self.serial.flushInput()
            self.serial.flushOutput()

        @set_timeout(1, mode='read')
        def get_readline():
            return self.serial.readline()

        for i in range(10):
            # print('compass init: {}'.format(i))
            response = ""
            while not len(response) >= 11:
                # response = self.serial.readline()
                try:
                    response = get_readline()
                except:
                    print('warning: cannot get init compass response')
            angle = self.bytesToAngle(response)
            self.angle = angle
        print('compass init finished')

    def bytesToAngle(self, U_Str):
        h = binascii.b2a_hex(U_Str)
        # a = str(h)[16:18] + str(h)[14:16]
        a = str(h)[-9:-7] + str(h)[-11:-9]
        a = int(a.upper(), 16)
        angle = 180 * a / 32768

        return angle

    def read(self):
        @set_timeout(1, mode='flush')
        def flushclear():
            self.serial.flushInput()
            self.serial.flushOutput()

        @set_timeout(1, mode='read')
        def get_readline():
            return self.serial.readline()

        try:
            flushclear()
        except:
            pass

        response = ""

        while response is None or not len(response) >= 11:
            try:
                response = get_readline()
            except:
                response = ""
                print('warning: cannot get compass response')
        angle = self.bytesToAngle(response)
        return angle

    def distribute_port(self):
        self.serial.flushInput()
        self.serial.flushOutput()
        stdtime = time.time()
        while time.time() - stdtime < 0.5:
            try:
                response = self.serial.readline()
                angle = self.bytesToAngle()
                if len(response) >= 11 and type(angle) is float:
                    return True
            except:
                pass
        return False


if __name__ == '__main__':
    print('test compass')
    compass = Compass(port=settings.compass_port)
    stdCompassAngle = compass.read()
    while True:
        print(compass.read())
