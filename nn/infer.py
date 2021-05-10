import cv2
import glob
import numpy as np
import paddle.fluid as fluid
from PIL import Image
import getopt
import matplotlib.pyplot as plt
from matplotlib.image import imread

model_save_dir = "deeplearning_car/model/model_infer"
params = "model_infer/params"
model = "model_infer/model"
infer_path = "deeplearning_car/data1/img/2162.jpg"
# infer_path = "1830.jpg"

pts1 = np.float32([[70, 0], [380, 0], [0, 232], [419, 237]])
pts2 = np.float32([[0, 0], [800, 0], [0, 700], [800, 700]])


def dataset(image_path):
    lower_hsv = np.array([20, 75, 165])
    upper_hsv = np.array([40, 255, 255])

    frame = cv2.imread(image_path)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask0 = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
    mask = mask0  #+ mask1

    img = Image.fromarray(mask)
    img = img.resize((128, 128), Image.ANTIALIAS)
    img = np.array(img).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img.transpose((2, 0, 1))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    np.savetxt('out.txt', mask, fmt="%d")  #保存为整数

    return img, mask


use_cuda = False
place = fluid.CUDAPlace(0) if use_cuda else fluid.CPUPlace()

infer_exe = fluid.Executor(place)
inference_scope = fluid.core.Scope()

#预测单张图片
with fluid.scope_guard(inference_scope):
    [inference_program,
     feed_target_names,
     target_var] = fluid.io.load_inference_model(model_save_dir,
                                                 infer_exe,
                                                 model_filename='model',
                                                 params_filename='params')
    img, mask = dataset(infer_path)

    results = infer_exe.run(program=inference_program,
                            feed={feed_target_names[0]: img},
                            fetch_list=target_var)
    print(results[0][0][0])

    img = imread(infer_path)  # 读入图像（设定合适的路径！）
    plt.imshow(img)
    plt.show()
