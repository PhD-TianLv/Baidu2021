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
ongoing_list['fortress1'] = 'complete'
ongoing_list['fortress2'] = 'complete'
ongoing_list['target1'] = 'complete'
ongoing_list['target2'] = 'complete'
ongoing_list['target3'] = 'complete'
ongoing_list['camping'] = 'complete'
ongoing_list['fenglangjuxu'] = 'complete'
settings.velocity = 10
ongoing_list['soldier'] = 'complete'

print("Init finished")

if ongoing_list['fortress2'] == 'complete':
    target1_stdtime = time.time()
if 'ongoing' not in ongoing_list.values():
    start_moving()
    pass

while True:
    front_image = front_camera.read()

    signResult = getMark(front_image, sign_predictor, mode='sign') if not task_lock.locked() else None

    if ongoing_list['fortress1'] != 'complete':
        if signResult and ongoing_list['fortress1'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fortress', task_name='fortress1')
        elif ongoing_list['fortress1'] == 'ongoing':
            # flag_name = turn_sideServo(work_side='left')
            flag_name = flag_names[0]
            fortress_task(flag_name, task_name='fortress1')
            start_moving()

    elif ongoing_list['fortress2'] != 'complete':
        if signResult and ongoing_list['fortress2'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fortress', task_name='fortress2')
        elif ongoing_list['fortress2'] == 'ongoing':
            # flag_name = turn_sideServo(work_side='right')
            flag_name = flag_names[1]
            fortress_task(flag_name, task_name='fortress2')
            start_moving()
            target1_stdtime = time.time()

    elif ongoing_list['target1'] != 'complete':
        if ongoing_list['target1'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='target', task_name='target1',
                                      continue_time=3, target1_stdtime=target1_stdtime)
        elif ongoing_list['target1'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 90, task_name='target')
            target_task(task_name='target1', direction='forward2backward')
            start_moving()

    elif ongoing_list['target2'] != 'complete':
        if signResult and ongoing_list['target2'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='target', task_name='target2',
                                      continue_time=1.7)
        elif ongoing_list['target2'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 90, task_name='target')
            target_task(task_name='target2', direction='forward2backward')
            start_moving()

    elif ongoing_list['target3'] != 'complete':
        if signResult and ongoing_list['target3'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='target', task_name='target3',
                                      continue_time=1.7)
        elif ongoing_list['target3'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 180, task_name='target')
            target_task(task_name='target3', direction='forward2backward')
            start_moving()

    elif ongoing_list['camping'] != 'complete':
        if signResult and ongoing_list['camping'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='barracks', task_name='camping')
        elif ongoing_list['camping'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 180, task_name='camping')
            camping_task()
            start_moving()

    elif ongoing_list['fenglangjuxu'] != 'complete':
        if signResult and ongoing_list['fenglangjuxu'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fenglangjuxu', task_name='fenglangjuxu',
                                      continue_time=1.7)
        elif ongoing_list['fenglangjuxu'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 270, task_name='fenglangjuxu')
            fenglangjuxu_task()
            # changeAnglePredictor()
            start_moving()

    elif ongoing_list['soldier'] != 'complete':
        if signResult and ongoing_list['soldier'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='soldier', task_name='soldier', continue_time=3)
        elif ongoing_list['soldier'] == 'ongoing':
            adjust_posture(settings.stdCompassAngle + 380, task_name='soldier')
            soldier_task()
            changeAnglePredictor()
            adjust_posture(settings.stdCompassAngle + 380, task_name='after_soldier')
            start_moving()

    elif ongoing_list['fortress3'] != 'complete':
        if signResult and ongoing_list['fortress3'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fortress', task_name='fortress3')
        elif ongoing_list['fortress3'] == 'ongoing':
            # flag_name = turn_sideServo(work_side='left')
            flag_name = flag_names[2]
            fortress_task(flag_name, task_name='fortress3')
            start_moving()
