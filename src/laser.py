import serial
import time
from threading import Thread


class Laser:
    def __init__(self, port):
        self.ser = serial.Serial()
        self.ser.port = "/dev/ttyUSB" + str(port)
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 1
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.writeTimeout = 2
        self.distance = -1

        try:
            self.ser.open()
        except Exception as e:
            raise Exception("error open serial port: " + str(e))

        self.run_flag = True
        self.start()

    def start(self):
        Thread(target=self.update, args=()).start()

    def stop(self):
        self.run_flag = False

    def read(self):
        return self.distance

    def update(self):
        while self.run_flag:
            response = self.ser.readline()
            try:
                self.distance = float(response.decode('utf-8'))
            except:
                pass


if __name__ == '__main__':
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
