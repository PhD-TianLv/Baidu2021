import paddle as pd
import paddle.fluid as fluid
import cv2
import numpy as np

place = fluid.CUDAPlace(0)
exe = fluid.Executor(place)


def load_model(model_dir='/home/aistudio/ssd-model',
               model_filename='mobilenet-ssd-model',
               params_filename='mobilenet-ssd-params'):
    [program, feed, fetch] = fluid.io.load_inference_model(
        model_dir,
        exe,
        model_filename=model_filename,
        params_filename=params_filename
    )
    return program, feed, fetch;


def ssd_preprocess(src):
    shape = [1, 3, 480, 480]
    img = cv2.resize(src, (480, 480))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img -= 127.5
    img *= 0.007843

    z = np.zeros((1, 480, 480, 3)).astype(np.float32)
    z[0, 0:img.shape[0], 0:img.shape[1] + 0, 0:img.shape[2]] = img
    z = z.reshape(1, 3, 480, 480)
    return z


def predict(data, program, feed, fetch):
    results = exe.run(
        program=program,
        feed={feed[0]: data},
        fetch_list=fetch,
        return_numpy=False
    )
    return np.array(results[0])


def analyse_res(res, class_num, label_list, score_thresold=0.7, debug=False):
    try:
        labels = res[:, 0]
        scores = res[:, 1]
    except:
        return []

    maxscore_index_per_class = [-1 for i in range(class_num)]
    maxscore_per_class = [-1 for i in range(class_num)]
    count = 0

    for label, score in zip(labels, scores):
        if score > maxscore_per_class[int(label)]:
            maxscore_per_class[int(label)] = score
            maxscore_index_per_class[int(label)] = count
        count += 1

    maxscore_index_per_class = [i for i in maxscore_index_per_class if i != -1]
    res = res[maxscore_index_per_class, :]
    results = []
    for item in res:
        label, score = item[0], item[1]
        label_name = label_list[int(label)]
        if debug:
            print(f'label_name = {label_name}, score = {score}')
        if score >= score_thresold:
            results.append([label_name, score])
    return results


def test_predict(label_list, model_dir, model_filename, params_filename, img_path):
    program, feed, fetch = load_model(model_dir)
    img = cv2.imread(img_path)
    data = ssd_preprocess(img)
    res = predict(data, program, feed, fetch)
    res = analyse_res(res=res, class_num=5, label_list=label_list, debug=True)
    print('finally res = {}'.format(res))


if __name__ == '__main__':
    label_list = [
        'daijun',
        'dingxiangjun',
        'dunhuang',
        'sideTarget',
        'targetCenter'
    ]
    model_dir = '/home/aistudio/ssd-model'
    model_filename = 'mobilenet-ssd-model'
    params_filename = 'mobilenet-ssd-params'
    img_path = '/home/aistudio/sideData1/dunhuang/png/1.png'

    test_predict(label_list, model_dir, model_filename, params_filename, img_path)