import os
import sys

# 车辆运行速度
velocity = 40

# collect.py 中数据的存储目录
resultDir = "train/"


def set_working_dir(__file__):
    work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    print('work_dir = {}'.format(work_dir))
    sys.path.clear()
    sys.path.append(work_dir)
    os.chdir(work_dir)
