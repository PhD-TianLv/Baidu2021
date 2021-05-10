import serial
from ctypes import *
import settings

comma_head_01_motor = bytes.fromhex('77 68 06 00 02 0C 02 01')
comma_head_02_motor = bytes.fromhex('77 68 06 00 02 0C 02 02')
comma_head_03_motor = bytes.fromhex('77 68 06 00 02 0C 02 03')
comma_head_04_motor = bytes.fromhex('77 68 06 00 02 0C 02 04')
comma_trail = bytes.fromhex('0A')
from serial_port import serial_connection


class Cart:
    def __init__(self):
        self.speed = 0
        self.angle = 0
        portx = "/dev/ttyUSB0"
        bps = 115200
        self.serial = serial.Serial(portx, int(bps), timeout=1, parity=serial.PARITY_NONE, stopbits=1)
        self.maxSpeed = 100
        self.minAngle = -2.0
        self.maxAngle = 2.0
        self.changeInAngle = settings.changeInAngle

    def steer(self, speed, angle):
        speed = int(speed) if speed else int(self.speed)
        angle = angle if angle else self.angle

        leftwheel = speed
        rightwheel = speed

        if angle < 0:
            leftwheel = int((1 + angle) * speed)
        if angle > 0:
            rightwheel = int((1 - angle) * speed)

        # print('angle = {}, leftwheel = {}, reightwhel = {}'.format(angle, leftwheel, rightwheel))  # DEBUG
        self.move([leftwheel, rightwheel, leftwheel, rightwheel])

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

    def move(self, speeds):
        left_front = int(speeds[0])
        right_front = -int(speeds[1])
        left_rear = int(speeds[2])
        right_rear = -int(speeds[3])

        left_front = self.exchange(left_front)
        right_front = self.exchange(right_front)
        left_rear = self.exchange(left_rear)
        right_rear = self.exchange(right_rear)

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


if __name__ == '__main__':
    cart = Cart()
    while True:
        cart.move([50, 100, 100, 100])
