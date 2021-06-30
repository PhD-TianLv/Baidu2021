import settings
import time
from camera import Camera
from cart import Cart
from cruiser import getAngle, init_predictor as init_angle_predictor
from marker import getResult as getMark, init_predictor as init_mark_predictor
from widgets import Servo_pwm, Light, Servo
from laser import Laser
from threading import Thread, Lock

front_camera = Camera(src=0)
side_camera = Camera(src=1, autoStart=False)
angle_predictor = init_angle_predictor()
sign_predictor = init_mark_predictor(settings.signModelPath)
task_predictor = init_mark_predictor(settings.taskModelPath)
cart = Cart()
cart.speed = settings.velocity
ongoing_list = settings.ongoing_list
task_lock = Lock()

light = Light(port=3)
servo_flag1 = Servo_pwm(3)
servo_flag2 = Servo_pwm(4)
servo_flag3 = Servo_pwm(5)
servo_flags = [servo_flag1, servo_flag2, servo_flag3]
sideServo = Servo(1)
sideServo.servocontrol(120, 50)


# 车道线识别
def moving():
    while ongoing_list['status'] != 'stop':
        if ongoing_list['status'] == 'slow_down':
            cart.speed = settings.slow_down_speed
        elif ongoing_list['status'] == 'run':
            cart.speed = settings.velocity
        front_image = front_camera.read()
        cart.angle = getAngle(front_image, angle_predictor)
        # print('status={},task_lock.locked={},angle={}'.format(ongoing_list['status'], task_lock.locked(), cart.angle))
        if not task_lock.locked():
            cart.steer(cart.speed, cart.angle)
    if not task_lock.locked():
        cart.stop()
    task_lock.release()
    print('movingThread has ended!')


def analyseSignResult(signResult):
    signResult = signResult[0]  # 同一时间只有一个地标
    label, score, bbox = signResult[0], signResult[1], signResult[2]
    xmin, ymin, xmax, ymax = bbox
    return label, score, xmin, ymin, xmax, ymax


def detect_slow_down_and_stop(signResult, true_label, task_name, continue_time=1.5):
    label, score, xmin, ymin, xmax, ymax = analyseSignResult(signResult)
    # print('ymin={}'.format(ymin))
    if label != true_label:
        return

    # 判断是否 stop
    if ymin > 0.8 and ongoing_list['status'] != 'stop':
        time.sleep(continue_time)  # 继续行驶直至小车车身覆盖住地标
        end_moving()

        ongoing_list[task_name] = 'ongoing'

        print('car stop, task ongoing')

    # 判断是否 slow_down
    elif ymin > 0.5 and ongoing_list['status'] != 'slow_down':
        ongoing_list['status'] = 'slow_down'
        print('car slow_down')


def turn_sideServo(work_side):
    side_camera.start()
    flag_list = list(settings.flag_to_servo.keys())

    if work_side == 'left':
        servo_angle = 120
    elif work_side == 'right':
        servo_angle = -60

    sideServo.servocontrol(30, 50)
    # print('turn sideServo')
    time.sleep(0.5)
    stdtime = time.time()
    sideServo.servocontrol(servo_angle, 25)
    while time.time() - stdtime < 7:
        side_image = side_camera.read()
        sideResult = getMark(side_image, task_predictor, mode='task')
        if not sideResult:
            continue
        label, score, xmin, ymin, xmax, ymax = analyseSignResult(sideResult)
        # print('label = {}, score = {}'.format(label, score))
        if label in flag_list:
            return label
    return "daijun"


def fortress_task(flag_name, task_name):
    servo_id = settings.flag_to_servo[flag_name]
    flag_servo = servo_flags[servo_id - 1]
    flag_servo.up()
    for i in range(3):
        light.lightgreen()
        time.sleep(1.5)
        light.lightoff()
        time.sleep(1.5)
    flag_servo.down()
    ongoing_list[task_name] = 'complete'


def target_task():
    laser_left = Laser(port=2)
    laser_right = Laser(port=1)
    cart.steer(8, 0)

    while True:
        dis_left, dis_right = float(laser_left.read()), float(laser_right.read())
        str_dis_left = "%.2f" % dis_left
        str_dis_right = "%.2f" % dis_right
        print('dis_left={}, dis_right={}'.format(str_dis_left, str_dis_right))
        if -1 in [dis_left, dis_right] or dis_left >= 0.5 or dis_right >= 0.5:
            continue
        if abs(dis_left - dis_right) <= 0.05:
            cart.stop()
            print('car stop')
            break


def start_moving():
    movingThread = Thread(target=moving, args=())
    ongoing_list['status'] = 'run'
    if task_lock.locked():
        task_lock.release()
    movingThread.start()
    print('start moving!')


def end_moving():
    ongoing_list['status'] = 'stop'
    task_lock.acquire()
    while task_lock.locked():
        pass
    cart.stop()
