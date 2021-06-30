import os
import sys

# -------global settings-------
# 车辆运行速度
velocity = 40
slow_down_speed = 15

# 工作目录
work_dir = '/home/root/workspace/Baidu2021'
lib_dir = './lib'

# -------collect.py-------
resultDir = "train/"
changeInAngle = 0.3
recordSideCam = False

# -------run_lane.py-------
angleModelPath = 'models/cruiseModel'

# -------marker.py--------
score_thresold = 0.7
flag_to_servo = {
    'dunhuang': 1,
    'daijun': 2,
    'dingxiangjun': 3
}
task_label_list = [
    'daijun',
    'dingxiangjun',
    'dunhuang',
    'sideTarget',
    'targetCenter'
]
sign_label_list = [
    'background',
    'barracks',
    'fenglangjuxu',
    'fortress',
    'soldier',
    'target',
]

signModelPath = 'models/signModel'  # train4
taskModelPath = 'models/taskModel'  # sideData2

# -------run.py--------
# TODO: 目前只有4个任务
ongoing_list = {  # uncomplete, ongoing, complete
    'fortress1': 'uncomplete',
    'fortress2': 'uncomplete',
    'target1': 'uncomplete',
    'target2': 'uncomplete',

    'status': 'run'  # run, slow_down, stop
}


def set_working_dir():
    print('work_dir = {}'.format(work_dir))
    os.chdir(work_dir)
    sys.path.append(work_dir)
    sys.path.append(lib_dir)


# 默认更改工作目录
set_working_dir()
