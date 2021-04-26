"""
此文件适用于 AI Studio 平台，可用于对模型做评估处理
"""

import os
import numpy as np
import cv2

cnn_args = {
    "shape": [1, 3, 128, 128],
    "ms": [125.5, 0.00392157]
}


class Predictor:
    """ base class for Predictor interface"""

    def load(self, j):
        """ load model """
        pass

    def set_input(self, data, index):
        """ set input at given index data is numpy array"""
        pass

    def get_output(self, index):
        """ output Tensor at given index can be cast into numpy array"""
        pass

    def run(self):
        """ do inference """
        pass


class PaddlePaddlePredictor(Predictor):
    """ PaddlePaddle interface wrapper """

    def __init__(self):
        import paddle as pd
        import paddle.fluid as fluid
        from paddle.fluid import debugger
        from paddle.fluid import core
        self.place = fluid.CUDAPlace(0)
        self.exe = fluid.Executor(self.place)

    def load(self, model_dir):
        import paddle.fluid as fluid
        # model_dir = j["model"]
        # print(colorize('Loading model: {}'.format(model_dir), fg='green'))
        program = None
        feed = None
        fetch = None
        print('model_dir = {}'.format(model_dir))
        if os.path.exists(model_dir + "/params"):
            [program, feed, fetch] = fluid.io.load_inference_model(
                model_dir, self.exe, model_filename='models', params_filename="params")
        else:
            print("not combined")
            [program, feed, fetch] = fluid.io.load_inference_model(model_dir, self.exe)

        self.program = program
        self.feed = feed
        self.fetch = fetch
        # print(self.program)
        self.inputs = [None] * len(self.feed)

    def set_input(self, data, index):
        self.inputs[index] = data

    def run(self):
        feeds = {}
        for index, _ in enumerate(self.inputs):
            feeds[self.feed[index]] = self.inputs[index]

        self.results = self.exe.run(program=self.program,
                                    feed=feeds, fetch_list=self.fetch, return_numpy=False)

        self.outputs = []
        for res in self.results:
            self.outputs.append(np.array(res))
        return self.results

    def get_output(self, index):
        return self.results[index]


# CNN网络的图片预处理
def process_image(frame, size, ms):
    frame = cv2.resize(frame, (size, size))
    img = frame.astype(np.float32)
    img = img - ms[0]
    img = img * ms[1]
    img = np.expand_dims(img, axis=0)
    return img;


# CNN网络预处理
def cnn_preprocess(args, img, buf):
    shape = args["shape"]
    img = process_image(img, shape[2], args["ms"]);
    hwc_shape = list(shape)
    hwc_shape[3], hwc_shape[1] = hwc_shape[1], hwc_shape[3]
    data = buf
    img = img.reshape(hwc_shape)
    # print("hwc_shape:{}".format(hwc_shape))
    data[0:, 0:hwc_shape[1], 0:hwc_shape[2], 0:hwc_shape[3]] = img
    data = data.reshape(shape)
    return data


# CNN网络预测
def infer_cnn(predictor, buf, image):
    data = cnn_preprocess(cnn_args, image, buf)
    predictor.set_input(data, 0)
    predictor.run()
    out = predictor.get_output(0)
    return np.array(out)[0][0]


class EvaCruiser():
    def __init__(self, cruise_model='cruise'):
        hwc_shape = list(cnn_args["shape"])
        hwc_shape[3], hwc_shape[1] = hwc_shape[1], hwc_shape[3]
        self.buf = np.zeros(hwc_shape).astype('float32')
        self.predictor = PaddlePaddlePredictor()
        self.predictor.load(cruise_model)

    def cruise(self, frame):
        res = infer_cnn(self.predictor, self.buf, frame)
        return res


c = EvaCruiser('cruise')
test_image = cv2.imread('73.jpg')
print(c.cruise(test_image))
