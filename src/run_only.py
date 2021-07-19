"""
注意事项：
**缺少一个旗帜舵机**
**车道线模型在有阴影的环境下不能正常行驶，需要再次训练**
1. 重新插拔 ttyUSB 以确定端口号
2. 小车启动时，一定要正着摆放，以获取磁罗盘初始角度值
3. 检查传感器时，注意旗子的位置，以防遮住激光雷达
4. 前置摄像头的线尽量往内收
"""
import settings
from run_algo import *

# 先校准磁罗盘
# 获取磁罗盘初始角度值，启动时一定要正着摆放
if settings.measureCompassAngle:
    settings.stdCompassAngle = compass.read()
print("stdCompassAngle = {}".format(settings.stdCompassAngle))

# camServo.center()
targetMotor.shrink()
light.lightoff()
flagServo1.down()
flagServo2.down()
flagServo3.down()
clipServo.loose()

flag_names = ['dunhuang', 'dingxiangjun', 'daijun']

# DEBUG
# ongoing_list['fortress1'] = 'complete'
# ongoing_list['fortress2'] = 'complete'
# ongoing_list['target1'] = 'complete'
# ongoing_list['target2'] = 'complete'
# ongoing_list['target3'] = 'complete'
# ongoing_list['camping'] = 'complete'
# ongoing_list['fenglangjuxu'] = 'complete'
# settings.velocity = 10
# ongoing_list['soldier'] = 'complete'

print("Init finished")

if ongoing_list['fortress2'] == 'complete':
    target1_stdtime = time.time()
if 'ongoing' not in ongoing_list.values():
    start_moving()
    pass

while True:
    front_image = front_camera.read()

    signResult = getMark(front_image, sign_predictor, mode='sign')

    if signResult and ongoing_list['fortress3'] == 'uncomplete':
        detect_slow_down_and_stop(signResult, true_label='soldier', task_name='soldier')
    elif ongoing_list['fortress3'] == 'ongoing':
        # flag_name = turn_sideServo(work_side='left')
        flag_name = flag_names[2]
        fortress_task(flag_name, task_name='fortress3')
        start_moving()
