"""
单运行巡航任务
"""
import settings
from camera import Camera
from cart import Cart
from cruiser import getAngle, init_predictor as init_angle_predictor

front_camera = Camera(src=0)
angle_predictor = init_angle_predictor()
cart = Cart()

cart.speed = settings.velocity

while True:
    front_image = front_camera.read()

    # DEBUG
    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)

    cart.angle = getAngle(front_image, angle_predictor)

    cart.steer(cart.speed, cart.angle)
