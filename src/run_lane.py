"""
单运行巡航任务
"""
import settings
from camera import Camera
from cart import Cart
from cruiser import getAngle, init_predictor as init_angle_predictor
from widgets import *
import cv2

front_camera = Camera(src=0)
angle_predictor = init_angle_predictor()
cart = Cart()


cart.speed = cart.velocity = settings.velocity = 20

while True:
    front_image = front_camera.read()
    cv2.imwrite('debug.jpg', front_image)

    # DEBUG
    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)

    cart.angle = getAngle(front_image, angle_predictor)
    print(cart.angle)
    cart.speed = cart.velocity + abs(cart.angle) * (cart.maxSpeed - cart.velocity) / 4

    cart.steer(cart.speed, cart.angle)
