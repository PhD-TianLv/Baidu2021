#%%
import cv2
import settings
import os
import numpy as np
from paddlelite import *


def img_deal(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 正常的 HSV
    lower_hsv = np.array([20, 75, 165])
    upper_hsv = np.array([40, 255, 255])

    # 阳光过强时的 HSV
    # lower_hsv = np.array([26, 43, 46])
    # upper_hsv = np.array([34, 255, 255])

    mask = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)

    frame = cv2.resize(mask, (128, 128))
    img = frame.astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img, mask


def init_predictor():
    valid_places = (
        Place(TargetType.kFPGA, PrecisionType.kFP16, DataLayoutType.kNHWC),
        Place(TargetType.kHost, PrecisionType.kFloat),
        Place(TargetType.kARM, PrecisionType.kFloat),
    )
    config = CxxConfig()
    model_dir = settings.angleModelPath
    if not os.path.exists(os.path.join(model_dir, "model")):
        raise Exception("model file does not exists")
    config.set_model_file(os.path.join(model_dir, "model"))
    if not os.path.exists(os.path.join(model_dir, "params")):
        raise Exception("params file does not exists")
    config.set_param_file(os.path.join(model_dir, "params"))
    config.set_valid_places(valid_places)
    predictor = CreatePaddlePredictor(config)
    return predictor


def angle_predict(img, predictor):
    buf = np.zeros((1, 128, 128, 3)).astype(np.float32)
    buf[0, 0:128, 0:128, 0:3] = img
    buf = buf.reshape((1, 3, 128, 128))

    input = predictor.get_input(0)
    input.resize((1, 3, 128, 128))
    input.set_data(buf)

    predictor.run()
    out = predictor.get_output(0)
    score = out.data()[0][0]
    return score


def test_cam():
    stream = cv2.VideoCapture(0)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    predictor = init_predictor()

    while True:
        _, frame = stream.read()
        # print(frame)
        img, mask = img_deal(frame)
        angle = angle_predict(img, predictor)
        print(angle)


if __name__ == '__main__':
    settings.set_working_dir()
    test_cam()
    '''
    predictor = init_predictor()
    
    # img = cv2.imread('480.jpg')
    img1_ori = cv2.imread('src/test/cruise/7.png')
    img2_ori = cv2.imread('src/test/cruise/13.png')
    img3_ori = cv2.imread('src/test/cruise/22.png')
    # print(img.shape)
    img1, mask = img_deal(img1_ori)
    angle = angle_predict(img1, predictor)

    num_img1 = img1_ori.copy()
    cv2.putText(num_img1, str(angle), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200), 5)

    # img = np.hstack([img1, num_img1])
    cv2.imwrite('num_img.jpg', num_img1)
    '''
