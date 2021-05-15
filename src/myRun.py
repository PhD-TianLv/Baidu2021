#%%
from camera import Camera
from cart import Cart
from myCruiser import img_deal, init_predictor, angle_predict
import settings
from cruiser import Cruiser
import cv2
import time
from widgets import Button, Buzzer
import json

settings.set_working_dir()

# 第一段完好程序

front_camera = Camera()
angle_predictor = init_predictor()
cart = Cart()

cart.speed = settings.velocity

while True:
    front_image = front_camera.read()
    img, mask = img_deal(front_image)

    # cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
    # cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)

    cart.angle = angle_predict(img, angle_predictor)

    cart.steer(cart.speed, cart.angle)

#
# def runAndSaveImage():
#     front_camera = Camera()
#     cart = Cart()
#     button_right = Button(1, 'RIGHT')
#     angle_predictor = init_predictor()
#     cruiser = Cruiser()
#
#     while True:
#         if button_right.clicked():
#             stdtime = time.time()
#             break
#
#     cnt = 0
#     while True:
#         front_image = front_camera.read()
#         img, mask = img_deal(front_image)
#         cv2.imwrite('debug/{}.jpg'.format(cnt), front_image)
#         cv2.imwrite('debug_hsv/{}.jpg'.format(cnt), mask)
#         cnt += 1
#
#         if 42 < time.time() - stdtime <= 52:
#             cart.speed = 40
#             cart.angle = cruiser.cruise(front_image)
#
#         else:
#             cart.speed = 40
#             cart.angle = angle_predict(img, angle_predictor)
#
#         cart.steer(cart.speed, cart.angle)
#
#
# def runTest():
#     front_camera = Camera()
#     cart = Cart()
#     cruiser = Cruiser()
#
#     while True:
#         front_image = front_camera.read()
#         cart.speed = 40  # speed change
#         cart.angle = cruiser.cruise(front_image)
#         cart.steer(cart.speed, cart.angle)
#
#
# def buttonThread(button_left):
#     while True:
#         if button_left.clicked():
#             buzzer = Buzzer()
#             path = 'train_test/result.json'
#             with open(path, 'w') as fp:
#                 json.dump(map.copy(), fp)
#             print('json data has been saved')
#             buzzer.rings()
#
#
# def runSaveData():
#     front_camera = Camera()
#     cart = Cart()
#     cruiser = Cruiser()
#     cnt = 0
#
#     while True:
#         front_image = front_camera.read()
#         # TODO
#         cart.speed = 40  # speed change
#         cart.angle = cruiser.cruise(front_image)
#         cart.steer(cart.speed, cart.angle)
#
#         cv2.imwrite('train_test/{}.jpg'.format(cnt), front_image)
#         map[cnt] = str(round(cart.angle, 4))
#
#
# runAndSaveImage()
# runTest()

# map = {}
# button_left = Button(1, "LEFT")
# Thread(target=buttonThread, args=(button_left,)).start()
# runSaveData()

# if __name__ == '__main__':
#     runAndSaveImage()

# runTest()
#
# global map
# map = {}
# button_left = Button(1, "LEFT")
# Thread(target=buttonThread, args=(button_left, map)).start()
# runSaveData(map)
