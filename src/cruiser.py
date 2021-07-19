#%%
import os
import settings
import cv2
import numpy as np
from paddlelite import Place, CxxConfig, CreatePaddlePredictor, TargetType, PrecisionType, DataLayoutType


def img_process(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 正常的 HSV
    lower_hsv = np.array([20, 75, 165])
    upper_hsv = np.array([40, 255, 255])

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
    print('model_dir = {}'.format(model_dir))
    if not os.path.exists(os.path.join(model_dir, "model")):
        raise Exception("model file does not exists")
    config.set_model_file(os.path.join(model_dir, "model"))
    if not os.path.exists(os.path.join(model_dir, "params")):
        raise Exception("params file does not exists")
    config.set_param_file(os.path.join(model_dir, "params"))
    config.set_valid_places(valid_places)
    predictor = CreatePaddlePredictor(config)
    return predictor


def predict_angle(img, predictor):
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


def getAngle(src, predictor):
    img, mask = img_process(src)
    angle = predict_angle(img, predictor)
    return angle


def test_cam():
    stream = cv2.VideoCapture(0)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    predictor = init_predictor()

    while True:
        _, frame = stream.read()
        # print(frame)
        img, mask = img_process(frame)
        angle = predict_angle(img, predictor)
        print(angle)


if __name__ == '__main__':
    test_cam()
