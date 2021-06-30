import numpy as np
import settings
import cv2
import os
from camera import Camera
from paddlelite import Place, CxxConfig, CreatePaddlePredictor, TargetType, PrecisionType, DataLayoutType


def init_predictor(model_dir=settings.signModelPath):
    valid_places = (
        Place(TargetType.kFPGA, PrecisionType.kFP16, DataLayoutType.kNHWC),
        Place(TargetType.kHost, PrecisionType.kFloat),
        Place(TargetType.kARM, PrecisionType.kFloat),
    )
    config = CxxConfig()
    if not os.path.exists(os.path.join(model_dir, "model")):
        raise Exception("model file does not exists")
    config.set_model_file(os.path.join(model_dir, "model"))
    if not os.path.exists(os.path.join(model_dir, "params")):
        raise Exception("params file does not exists")
    config.set_param_file(os.path.join(model_dir, "params"))
    config.set_valid_places(valid_places)
    predictor = CreatePaddlePredictor(config)
    return predictor


def infer_ssd(predictor, img, data):
    input = predictor.get_input(0)
    input.resize(data.shape)
    input.set_data(data)

    predictor.run()
    out = predictor.get_output(0)
    return np.array(out)


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


def analyse_res(res, mode, debug=False,
                score_thresold=settings.score_thresold):
    if mode == 'sign':
        label_list = settings.sign_label_list
    elif mode == 'task':
        label_list = settings.task_label_list
    else:
        raise Exception("mode must in ['sign', 'task']")

    class_num = len(label_list)

    try:
        labels = res[:, 0]
        scores = res[:, 1]
    except:
        return []

    maxscore_index_per_class = [-1 for i in range(class_num)]
    maxscore_per_class = [-1 for i in range(class_num)]
    count = 0

    for label, score in zip(labels, scores):
        if label > len(label_list) - 1:
            continue
        if score > maxscore_per_class[int(label)]:
            maxscore_per_class[int(label)] = score
            maxscore_index_per_class[int(label)] = count
        count += 1

    maxscore_index_per_class = [i for i in maxscore_index_per_class if i != -1]
    res = res[maxscore_index_per_class, :]
    results = []
    for item in res:
        label, score, bbox = item[0], item[1], list(item[2:])
        label_name = label_list[int(label)]
        if debug:
            print('label_name = {}, score = {}'.format(label_name, score))
        if score >= score_thresold:
            results.append([label_name, score, bbox])
    return results


def getResult(img, predictor, mode):
    """
    bbox: xmin,ymin,xmax,ymax
    """
    data = ssd_preprocess(img)
    res = infer_ssd(predictor, img, data)
    result = analyse_res(res, mode=mode)
    return result


def test_camera(mode):
    if mode == 'sign':
        camera_id = 0
        model_dir = settings.signModelPath
    elif mode == 'task':
        camera_id = 1
        model_dir = settings.taskModelPath
    else:
        raise Exception("mode must in ['sign', 'task']")

    front_camera = Camera(src=camera_id)
    predictor = init_predictor(model_dir=model_dir)

    # badDataCnt = 0
    while True:
        img = front_camera.read()

        result = getResult(img, predictor, mode)

        if result:
            print(result)

            # Collect
            # badDataCnt += 1
            # '.format(badDataCnt), img)


def test_img(mode):
    if mode == 'sign':
        model_dir = settings.signModelPath
    elif mode == 'task':
        model_dir = settings.taskModelPath
    else:
        raise Exception("mode must in ['sign', 'task']")

    predictor = init_predictor(model_dir=model_dir)
    src = cv2.imread('test_imgs/testSign_barracks.png')
    assert src is not None, "Failed to read image"

    # # DEBUG
    # data = ssd_preprocess(src)
    # res = infer_ssd(predictor, src, data)
    # print(res)

    result = getResult(src, predictor, mode)
    print(result)


if __name__ == '__main__':
    import settings

    # test_camera(mode='task')

    test_img(mode='sign')
