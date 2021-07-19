import serial

from ctypes import *
from widgets import serial_connection
import settings
import time
from compass_prepare import Compass

comma_head_01_motor = bytes.fromhex('77 68 06 00 02 0C 02 01')
comma_head_02_motor = bytes.fromhex('77 68 06 00 02 0C 02 02')
comma_head_03_motor = bytes.fromhex('77 68 06 00 02 0C 02 03')
comma_head_04_motor = bytes.fromhex('77 68 06 00 02 0C 02 04')
comma_trail = bytes.fromhex('0A')


class Cart:
    def __init__(self):
        self.velocity = settings.velocity
        self.speed = 0
        self.angle = 0
        portx = "/dev/" + str(settings.wobot_port)
        print('cart_port = {}'.format(portx))
        bps = 115200
        self.serial = serial.Serial(portx, int(bps), timeout=1, parity=serial.PARITY_NONE, stopbits=1)
        self.maxSpeed = 100
        self.minAngle = -2.0
        self.maxAngle = 2.0
        self.changeInAngle = settings.changeInAngle

        time.sleep(0.5)

        self.force_stop()

    def steer(self, speed, angle):
        speed = int(speed) if speed else int(self.speed)
        angle = angle if angle else self.angle

        leftwheel = speed
        rightwheel = speed

        if angle < 0:
            leftwheel = int((1 + angle) * speed)
        elif angle > 0:
            rightwheel = int((1 - angle) * speed)

        # print('angle = {}, leftwheel = {}, reightwhel = {}'.format(angle, leftwheel, rightwheel))  # DEBUG
        self.move([leftwheel, rightwheel, leftwheel, rightwheel])

    def force_steer(self, speed, angle):
        for i in range(4):
            self.steer(speed, angle)
        stdtime = time.time()
        while time.time() - stdtime < 0.1:
            self.steer(speed, angle)
            time.sleep(0.01)

    def force_stop(self):
        self.move([0, 0, 0, 0])
        stdtime = time.time()
        while time.time() - stdtime < 0.1:
            self.move([0, 0, 0, 0])
            time.sleep(0.01)
        self.speed = 0
        self.angle = 0

    def stop(self):
        self.move([0, 0, 0, 0])
        self.speed = 0
        self.angle = 0

    def exchange(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        else:
            speed = speed
        return speed

    def force_move(self, speeds):
        for i in range(4):
            self.move(speeds)

        stdtime = time.time()
        while time.time() - stdtime < 0.1:
            self.move(speeds)
            time.sleep(0.01)

    def move(self, speeds):
        left_front = int(speeds[0])
        right_front = -int(speeds[1])
        left_rear = int(speeds[2])
        right_rear = -int(speeds[3])

        left_front = self.exchange(left_front)
        right_front = self.exchange(right_front)
        left_rear = self.exchange(left_rear)
        right_rear = self.exchange(right_rear)
        # print('left_front = {}, right_front = {}, left_rear = {}, right_rear = {}'.format(left_front, right_front,
        #                                                                                   left_rear, right_rear))

        send_data_01_motor = comma_head_01_motor + left_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_02_motor = comma_head_02_motor + right_front.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_03_motor = comma_head_03_motor + left_rear.to_bytes(1, byteorder='big', signed=True) + comma_trail
        send_data_04_motor = comma_head_04_motor + right_rear.to_bytes(1, byteorder='big', signed=True) + comma_trail
        # print(send_data_01_motor)  # DEBUG

        self.serial.write(send_data_01_motor)
        self.serial.write(send_data_02_motor)
        self.serial.write(send_data_03_motor)
        self.serial.write(send_data_04_motor)

    def turn_left(self):
        speed = self.speed
        leftwheel = -speed
        rightwheel = speed
        self.move([leftwheel, rightwheel, leftwheel, rightwheel])

    def turn_right(self):
        speed = self.speed
        leftwheel = speed
        rightwheel = -speed

        self.move([leftwheel, rightwheel, leftwheel, rightwheel])

    def reverse(self):
        speed = self.speed
        self.move([-speed, -speed, -speed, -speed])

    def posture_move(self, bias):
        """
        drivetime -> distance (speed = 15)
        0.5 -> 0.9
        0.7 -> 1.6
        0.8 -> 2.0
        0.9 -> 2.6
        1	-> 4.3
        1.5 -> 7.1
        """
        # bias > 0 表示向右移, bias < 0 表示向左移
        if bias == 0:
            return

        if abs(bias) > 7.1:
            drivetime = 1.5
        elif abs(bias) > 4.3:
            drivetime = 1
        elif abs(bias) > 2.6:
            drivetime = 0.9
        elif abs(bias) > 2.0:
            drivetime = 0.8
        elif abs(bias) > 1.6:
            drivetime = 0.7
        elif abs(bias) > 0.9:
            drivetime = 0.5
        else:
            return

        if bias > 0:
            self.force_move([-15, 0, -15, 0])
            time.sleep(drivetime)
            self.force_move([0, -15, 0, -15])
            time.sleep(drivetime)
            self.force_move([15, 15, 15, 15])
            time.sleep(drivetime)
            self.force_stop()
        elif bias < 0:
            self.force_move([0, -15, 0, -15])
            time.sleep(drivetime)
            self.force_move([-15, 0, -15, 0])
            time.sleep(drivetime)
            self.force_move([15, 15, 15, 15])
            time.sleep(drivetime)
            self.force_stop()

    def turnToCompassAngle(self, angle, compass):
        # print("Compass DEBUG!!!")
        # return  # DEBUG

        angle %= 360
        # compass.start()
        print('target_angle = {}'.format(angle))
        print("start_angle = {}".format(compass.read()))
        # 如果相差 4° 以上，则手动加大偏转角度
        if 4 <= compass.read() - angle < 12 or -356 <= compass.read() - angle < -348:
            for i in range(4):
                self.move([-15, 15, -15, 15])  # 往右转，增大偏转角
                time.sleep(0.0001)
            stdtime = time.time()
            while 4 <= compass.read() - angle < 12 or -356 <= compass.read() - angle < -348:
                if time.time() - stdtime > 4:
                    cart.force_steer(40, 0)
                    time.sleep(0.5)
                    break  # 防卡顿
                # print(compass.read())
                pass
            # print('last1_angle = {}'.format(compass.read()))
            self.move([0, 0, 0, 0])
            # print('last2_angle = {}'.format(compass.read()))
            for i in range(4):
                self.move([0, 0, 0, 0])
                time.sleep(0.0001)
            self.force_stop()
            # print('last3_angle = {}'.format(compass.read()))
        if -12 < compass.read() - angle <= -4 or 348 <= compass.read() - angle < 356:
            for i in range(4):
                self.move([15, -15, 15, -15])
                time.sleep(0.0001)
            stdtime = time.time()
            while -12 <= compass.read() - angle < -4 or 348 < compass.read() - angle <= 356:
                if time.time() - stdtime > 4:
                    cart.force_steer(40, 0)
                    time.sleep(0.5)
                    break  # 防卡顿
                # print(compass.read())
                pass
            # print('last1_angle = {}'.format(compass.read()))
            self.move([0, 0, 0, 0])
            # print('last2_angle = {}'.format(compass.read()))
            for i in range(4):
                self.move([0, 0, 0, 0])
                time.sleep(0.0001)
            self.force_stop()
            # print('last3_angle = {}'.format(compass.read()))

        time.sleep(0.5)

        # 往左转
        if 9 <= compass.read() - angle < 40 or -351 <= compass.read() - angle < -311:
            for i in range(4):
                self.move([15, -15, 15, -15])
                time.sleep(0.0001)
            stdtime = time.time()
            while 9 <= compass.read() - angle < 40 or -351 <= compass.read() - angle <= -311:
                if time.time() - stdtime > 4:
                    cart.force_steer(40, 0)
                    time.sleep(0.5)
                    break  # 防卡顿
                # print(now_angle)
                pass
            print('last1_angle = {}'.format(compass.read()))
            self.move([0, 0, 0, 0])
            print('last2_angle = {}'.format(compass.read()))
            for i in range(4):
                self.move([0, 0, 0, 0])
                time.sleep(0.0001)
            self.force_stop()
            print('last3_angle = {}'.format(compass.read()))
        # 往右转
        elif -40 < compass.read() - angle <= -9 or 311 < compass.read() - angle <= 351:
            for i in range(4):
                self.move([-15, 15, -15, 15])
                time.sleep(0.0001)
            stdtime = time.time()
            while -40 <= compass.read() - angle <= -9 or 311 <= compass.read() - angle <= 351:
                if time.time() - stdtime > 4:
                    cart.force_steer(40, 0)
                    time.sleep(0.5)
                    break  # 防卡顿
                # print(now_angle)
                pass
            print('last1_angle = {}'.format(compass.read()))
            self.move([0, 0, 0, 0])
            print('last2_angle = {}'.format(compass.read()))
            for i in range(4):
                self.move([0, 0, 0, 0])
                time.sleep(0.0001)
            print('last3_angle = {}'.format(compass.read()))
        print('last_angle = {}'.format(compass.read()))
        # compass.stop()


if __name__ == '__main__':
    cart = Cart()
    while True:
        cart.move([15, 15, 15, 15])
