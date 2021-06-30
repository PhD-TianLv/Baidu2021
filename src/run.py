#%%
from run_algo import *

light.lightoff()
servo_flag1.down()
servo_flag2.down()
servo_flag3.down()

# DEBUG
ongoing_list['fortress1'] = 'complete'
ongoing_list['fortress2'] = 'complete'

print("Init finished")

start_moving()

while True:
    front_image = front_camera.read()

    signResult = getMark(front_image, sign_predictor, mode='sign') if not task_lock.locked() else None

    if ongoing_list['fortress1'] != 'complete':
        if signResult and ongoing_list['fortress1'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fortress', task_name='fortress1')
        elif ongoing_list['fortress1'] == 'ongoing':
            flag_name = turn_sideServo(work_side='left')
            fortress_task(flag_name, task_name='fortress1')
            start_moving()

    elif ongoing_list['fortress2'] != 'complete':
        if signResult and ongoing_list['fortress2'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='fortress', task_name='fortress2')
        elif ongoing_list['fortress2'] == 'ongoing':
            flag_name = turn_sideServo(work_side='right')
            fortress_task(flag_name, task_name='fortress2')
            start_moving()

    elif ongoing_list['target1'] != 'complete':
        if signResult and ongoing_list['target1'] == 'uncomplete':
            detect_slow_down_and_stop(signResult, true_label='target', task_name='target1', continue_time=1.2)
        elif ongoing_list['target1'] == 'ongoing':
            target_task()
