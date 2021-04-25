import threading

# 若不连接 WOBOT 控制器，则注释以下内容
from serial_port import serial_connection
from widgets import Light, Servo, Motor_rotate
from cart import Cart

serial = serial_connection

from joystick import JoyStick
from cruiser import Cruiser
from camera import Camera

from config import front_cam

import cv2
import time


def Lightwork(light_port, color):
    light = Light(light_port)
    red = [80, 0, 0]
    green = [0, 80, 0]
    yellow = [80, 80, 0]
    off = [0, 0, 0]
    light_color = [0, 0, 0]
    if color == 'red':
        light_color = red
    elif color == 'green':
        light_color = green
    elif color == 'yellow':
        light_color = yellow
    elif color == 'off':
        light_color = off
    light.lightcontrol(0, light_color[0], light_color[1], light_color[2])


def test_light():
    # TODO
    pass


def test_motor(port=1):
    motor = Motor_rotate(port)
    while True:
        motor.motor_rotate(50)


def test_servo(ID=1):
    servo = Servo(ID)
    while True:
        servo.servocontrol(-60, 50)
        time.sleep(0.5)
        servo.servocontrol(60, 50)
        time.sleep(0.5)


def test_joystick():
    js = JoyStick()
    js.open()
    while True:
        time, value, type_, number = js.read()
        print('-' * 32)
        print('time = {}'.format(time))
        print('value = {}'.format(value))
        print('type_ = {}'.format(type_))
        print('number = {}'.format(number))
        print('x_axis = {}'.format(js.get_x_axis()))


def test_img_cruiseModel():
    cruiser = Cruiser()
    img = cv2.imread('test/cruise/7.png')
    # print(img.shape)
    print('angle = {}'.format(cruiser.cruise(img)))


def test_cam_cruiseModel():
    cruiser = Cruiser()
    front_camera = Camera(front_cam, [640, 480])
    front_camera.start()

    while True:
        front_image = front_camera.read()
        cv2.imwrite('front_image.jpg', front_image)
        print('angle = {}'.format(cruiser.cruise(front_image)))


def test_sign():
    # TODO: Complete the task
    cruiser = Cruiser()
    front_camera = Camera(front_cam, [640, 480])
    front_camera.start()

    while True:
        front_image = front_camera.read()
        cv2.imwrite('front_image.jpg', front_image)


def test_cart():
    cart = Cart()
    while True:
        cart.steer(speed=50, angle=1)
        # cart.move([-50, 50, -50, 50])
        # cart.move([0, 0, 0, 50])


def test_thread():
    while True:
        print('open thread')


def joystick_thread(js, cart):
    while True:
        time, value, type_, number = js.read()
        # Key = X | speed = 80
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = 50
            print('Key[X] down, run at {}'.format(cart.speed))

        # Key = B | stop | keep the value of angle
        if type_ == 1 and number == 1 and value == 1:
            cart.speed = 0
            print('Key[B] down, stop')

        # Key = Y | angle = 0
        if type_ == 1 and number == 4 and value == 1:
            cart.angle = 0
            print('Key[Y] down, angle = 0')

        # Key = LEFT | angle -= 0.25
        if type_ == 2 and number == 6 and value == -32767:
            if cart.angle == -2.0:
                print('Key[LEFT] down, angle == -2.0, maximizing')
            else:
                cart.angle -= 0.25
                print('Key[LEFT] down, angle -= 0.25, now angle = {}'.format(cart.angle))

        # Key = RIGHT | angle += 0.25
        if type_ == 2 and number == 6 and value == 32767:
            if cart.angle == 2.0:
                print('Key[RIGHT] down, angle == 2.0, maximizing')
            else:
                cart.angle += 0.25
                print('Key[RIGHT] down, angle += 0.25, now angle = {}'.format(cart.angle))


def test_joystick_run():
    # init
    js = JoyStick()
    js.open()
    cart = Cart()
    cart.angle = 0
    cart.velocity = 0
    js_thread = threading.Thread(target=joystick_thread, args=(js, cart,))
    js_thread.start()
    print('Init complete, wait for instruction')

    while True:
        cart.steer(cart.velocity, cart.angle)

    js_thread.join()
    cart.stop()


if __name__ == '__main__':
    # test_motor(1)
    # test_joystick()
    # test_cam_cruiseModel()
    test_cart()
    # test_img_cruiseModel()
    # test_joystick_run()
