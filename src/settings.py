import os
import sys

# -------global settings-------
# 车辆运行速度
velocity = 40

# 工作目录
work_dir = '/home/root/workspace/Baidu2021'

# -------collect.py-------
resultDir = "train/"
angleModelPath = 'models/cruiseModel'
changeInAngle = 0.3
recordSideCam = False


def set_working_dir():
    print('work_dir = {}'.format(work_dir))
    sys.path.clear()
    sys.path.append(work_dir)
    os.chdir(work_dir)
