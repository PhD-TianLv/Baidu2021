import paddlemobile as pm
from PIL import Image
import numpy as np


def deal_tensor(label_img):
    tensor_img = label_img.resize((256, 256), Image.BILINEAR)
    if tensor_img.mode != 'RGB':
        tensor_img = tensor_img.convert('RGB')
    tensor_img = np.array(tensor_img).astype('float32').transpose((2, 0, 1))
    tensor_img -= 127.5
    tensor_img *= 0.007843
    tensor_img = tensor_img[np.newaxis, :]
    tensor = pm.PaddleTensor()
    tensor.dtype = pm.PaddleDType.FLOAT32
    tensor.shape = (1, 3, 256, 256)
    tensor.data = pm.PaddleBuf(tensor_img)
    paddle_data_feeds = [tensor]
    return paddle_data_feeds
