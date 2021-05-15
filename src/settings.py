import os
import sys

# 车辆运行速度
# velocity = 40
velocity = 25

# collect.py 中数据的存储目录
resultDir = "train/"

angleModelPath = 'models/cruiseModel'

changeInAngle = 0.1


def set_working_dir():
    work_dir = '/home/root/workspace/Baidu2021'
    print('work_dir = {}'.format(work_dir))
    sys.path.clear()

    sys.path.append(work_dir)
    os.chdir(work_dir)
