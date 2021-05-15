#%%
from camera import Camera
from cart import Cart
from myCruiser import img_deal, init_predictor, angle_predict
import settings
from cruiser import Cruiser
import cv2
import time
from widgets import Button

settings.set_working_dir()

# 第一段完好程序
front_camera = Camera()
angle_predictor = init_predictor()
cart = Cart()

cart.speed = settings.velocity

# DEBUG
# 保存图片


cnt = 0
while True:
    print('ok')
    front_image = front_camera.read()
    img, mask = img_deal(front_image)

    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)
    cnt += 1

    cart.angle = angle_predict(img, angle_predictor)

    print('cnt = {}, angle = {}'.format(cnt, cart.angle))
    cart.steer(cart.speed, cart.angle)
# # 应急程序
#
# front_camera = Camera()
# cruiser = cruiser()
# cart = Cart
#
# while True:
#     front_image = front_camera.read()
#     cart.angle = cruiser.cruise(front_image)
#     print(cart.angle)
#     # cart.steer(cart.speed, cart.angle)
#
#
# front_camera = Camera()
# cart = Cart()
# button_right = Button(1, 'RIGHT')
# angle_predictor = init_predictor()
# cruiser = Cruiser()
# # while True:
# run_flag = True
# while run_flag:
#     if button_right.clicked():
#         stdtime = time.time()
#         print(stdtime)
#         break
#
# print('here')
#
# while run_flag:
#     front_image = front_camera.read()
#     # print("{:.2f}".format(time.time() - stdtime)) # DEBUG
#
#     if 41.5 < time.time() - stdtime <= 51:
#         print('change')
#         cart.speed = 25
#         cart.angle = cruiser.cruise(front_image)
#     #
#     else:
#         cart.speed = 40
#         img, mask = img_deal(front_image)
#         cart.angle = angle_predict(img, angle_predictor)
#
#     # cart.speed = 25
#     # cart.angle = cruiser.cruise(front_image)
#     # img, mask = img_deal(front_image)
#     # cart.angle = angle_predict(img, angle_predictor)
#     # print(cart.angle)
#
#     cart.steer(cart.speed, cart.angle)