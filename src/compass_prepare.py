import binascii
import signal
from threading import Thread, Lock
import serial
import time
import settings


class Compass:
    def __init__(self, init_flag=True):
        portx_old = "/dev/compass_old"
        portx_new = "/dev/compass_new"
        bps = 115200
        self.old_serial = serial.Serial(portx_old,
                                        int(bps),
                                        bytesize=serial.EIGHTBITS,
                                        timeout=0.001,  # 不许改动
                                        parity=serial.PARITY_NONE,
                                        stopbits=1,
                                        xonxoff=False,
                                        rtscts=False,
                                        dsrdtr=False,
                                        writeTimeout=1)
        self.new_serial = serial.Serial(portx_new,
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
        self.read_lock = Lock()
        self.old_response = self.new_response = ""

        try:
            self.new_serial.open()
            self.old_serial.open()
        except Exception as e:
            if not str(e) == 'Port is already open.':
                raise Exception("error open serial port: " + str(e))

        # 初始化
        if init_flag:
            self.initialize()

    def initialize(self):
        for i in range(10):
            print(self.read())
        print("compass init finished")

    def bytesToAngle(self, U_Str):
        h = binascii.b2a_hex(U_Str)
        # a = str(h)[16:18] + str(h)[14:16]
        a = str(h)[-9:-7] + str(h)[-11:-9]
        a = int(a.upper(), 16)
        angle = 180 * a / 32768
        return angle

    # @set_timeout(1, mode='newCompass_flush')
    def newCompassFlushClear(self):
        self.new_serial.flushInput()
        self.new_serial.flushOutput()

    # @set_timeout(1, mode='oldCompass_flush')
    def oldCompassFlushClear(self):
        self.old_serial.flushInput()
        self.old_serial.flushOutput()

    # @set_timeout(1, mode='newCompass_read')
    def newCompass_getReadline(self):
        try:
            self.new_response = self.new_serial.readline()
        except:
            pass

    # @set_timeout(1, mode='oldCompass_read')
    def oldCompass_getReadline(self):
        try:
            self.old_response = self.old_serial.readline()
        except:
            pass

    # @set_timeout(1, mode='oldCompassReadThread')
    def oldCompassReadThread(self):
        self.oldCompassFlushClear()
        self.old_response = ""
        while self.old_response is None or len(self.old_response) < 11:
            self.oldCompass_getReadline()
        self.angle = self.bytesToAngle(self.old_response)

    # @set_timeout(1, mode='newCompassReadThread')
    def newCompassReadThread(self):
        self.newCompassFlushClear()
        self.new_response = ""
        while self.new_response is None or len(self.new_response) < 11:
            self.newCompass_getReadline()
        self.angle = self.bytesToAngle(self.new_response)

    def read(self):
        self.angle = -1
        Thread(target=self.newCompassReadThread).start()
        Thread(target=self.oldCompassReadThread).start()
        if self.angle != -1 and self.angle is not None:
            return self.angle


if __name__ == '__main__':
    print('test compass')
    compass = Compass()
    stdCompassAngle = compass.read()
    while True:
        print(compass.read())
