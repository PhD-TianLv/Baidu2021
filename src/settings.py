import os
import sys

# -------global settings-------
# 设置是否自动测量 stdCompassAngle
measureCompassAngle = False
# 现在是设置为手动测量
stdCompassAngle = 270

target_posture_range = (0, 1.5)
camping_posture_range = (-1.5, 0)
fenglangjuxu_posture_range = (1, 3)
soldier_posture_range = (2.5, 3)
after_soldier_posture_range = (-6, -4)

# 车辆运行速度
velocity = 15
slow_down_speed = 15
# 中途更换模型后的调整速度
changeAngleVelocity = 20

# 工作目录
work_dir = '/home/root/workspace/Baidu2021'
lib_dir = './lib'

# 传感器端口号
wobot_port = "wobot"
laser_square_port = "laser_square"
laser_ball_port = "laser_ball"
laser1_port = "laser1"
laser2_port = "laser2"
compass_port = "compass"

# -------collect.py-------
resultDir = "train/"
changeInAngle = 0.1
recordSideCam = False

# -------run_lane.py-------
# train7可以跑过两个急转弯
angleModelPath = 'models/train9'

# -------marker.py--------
score_thresold = 0.7
flag_to_servo = {
    'dingxiangjun': 1,
    'daijun': 2,
    'dunhuang': 3
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

signModelPath = 'models/signModel'
taskModelPath = 'models/taskModel'  # sideData2

# -------run.py--------
ongoing_list = {  # uncomplete, ongoing, complete
    'fortress1': 'uncomplete',
    'fortress2': 'uncomplete',
    'target1': 'uncomplete',
    'target2': 'uncomplete',
    'target3': 'uncomplete',
    'camping': 'uncomplete',
    'fenglangjuxu': 'uncomplete',
    'soldier': 'uncomplete',
    'fortress3': 'uncomplete',

    'status': 'run',  # run, slow_down, stop
    'last_center_x': -1
}


def set_working_dir():
    print('work_dir = {}'.format(work_dir))
    os.chdir(work_dir)
    sys.path.append(work_dir)
    sys.path.append(lib_dir)


# 默认更改工作目录
set_working_dir()
