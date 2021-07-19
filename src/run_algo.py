from cart import Cart
import settings
import time
from camera import Camera
from cruiser import getAngle, init_predictor as init_angle_predictor
from marker import getResult as getMark, init_predictor as init_mark_predictor
from widgets import SoldierServo, FlagServo, ClipServo, Light, CamServo, BottomServo, SideMotor
from widgets import Servo, Servo_pwm
from laser import Laser
from laser_bool import LaserBool
from compass import Compass
from threading import Thread, Lock

front_camera = Camera(src=0)
# side_camera = Camera(src=1, autoStart=False)
angle_predictor = init_angle_predictor()
sign_predictor = init_mark_predictor(settings.signModelPath)
task_predictor = init_mark_predictor(settings.taskModelPath)
cart = Cart()
cart.speed = settings.velocity
ongoing_list = settings.ongoing_list
task_lock = Lock()

light = Light(port=3)
flagServo1 = FlagServo(3)
flagServo2 = FlagServo(4)
flagServo3 = FlagServo(5)
servo_flags = [flagServo1, flagServo2, flagServo3]
targetMotor = SideMotor(8)
# camServo = camServo(9)
bottomServo = BottomServo(2)
clipServo = ClipServo(1)
soldierServo = SoldierServo(6)

# 注意 Laser 的端口号，尽量重启而不改变端口号
compass = Compass(port=settings.compass_port)
laser_up = Laser(port=settings.laser1_port)
laser_down = Laser(port=settings.laser2_port)

laser_square = LaserBool(port=settings.laser_square_port)
laser_ball = LaserBool(port=settings.laser_ball_port)


def changeAnglePredictor():
    # 由于模型异常，需要在中途更换角度预测模型
    settings.angleModelPath = 'models/train9'
    angle_predictor = init_angle_predictor()
    cart.velocity = cart.speed = settings.changeAngleVelocity


# 车道线识别
def moving():
    while ongoing_list['status'] != 'stop':
        front_image = front_camera.read()
        cart.angle = getAngle(front_image, angle_predictor)
        if ongoing_list['status'] == 'slow_down':
            cart.speed = settings.slow_down_speed
        elif ongoing_list['status'] == 'target1_slow_down':
            cart.speed = 8
        elif ongoing_list['status'] == 'run':
            # cart.speed = cart.velocity
            cart.speed = cart.velocity + abs(cart.angle) * (cart.maxSpeed - cart.velocity) / 4
        # print('status={},task_lock.locked={},angle={}'.format(ongoing_list['status'], task_lock.locked(), cart.angle))
        if not task_lock.locked():
            # print('angle = {}'.format(cart.angle))  # DEBUG
            cart.steer(cart.speed, cart.angle)
    if not task_lock.locked():
        cart.force_stop()
    task_lock.release()
    print('movingThread has ended!')


def detect_last_center_x():
    while True:
        front_image = front_camera.read()
        signResult = getMark(front_image, sign_predictor, mode='sign')
        # print(signResult)
        if not signResult:
            break
        xmin, xmax = signResult[0][2][0], signResult[0][2][2]
        ongoing_list['last_center_x'] = (xmin + xmax) / 2


def analyseSignResult(signResult):
    signResult = signResult[0]  # 同一时间只有一个地标
    label, score, bbox = signResult[0], signResult[1], signResult[2]
    xmin, ymin, xmax, ymax = bbox
    return label, score, xmin, ymin, xmax, ymax


def detect_slow_down_and_stop(signResult, true_label, task_name, continue_time=2.5, target1_stdtime=None):
    # 过 打靶 1 的十字路口，放缓速度
    if task_name == 'target1' and 1.5 < time.time() - target1_stdtime <= 4:
        ongoing_list['status'] = 'slow_down'
    elif task_name == 'target1' and time.time() - target1_stdtime > 5:
        ongoing_list['status'] = 'run'

    if not signResult:
        return
    label, score, xmin, ymin, xmax, ymax = analyseSignResult(signResult)

    # print('ymin={}'.format(ymin))
    if label != true_label:
        return
    elif task_name == 'target1' and time.time() - target1_stdtime < 7:
        return

    # print("ymin = {}".format(ymin))

    # 判断是否 stop
    if ymin > 0.5 and ongoing_list['status'] != 'stop':
        if task_name == 'target1':
            ongoing_list['status'] = 'target1_slow_down'
        time.sleep(continue_time)  # 继续行驶直至小车车身覆盖住地标
        end_moving()

        ongoing_list[task_name] = 'ongoing'
        cart.stop()
        print('car stop, task {} ongoing'.format(task_name))

    # 判断是否 slow_down
    elif ymin > 0.25 and ongoing_list['status'] != 'slow_down':
        ongoing_list['status'] = 'slow_down'
        print('car slow_down')
        # 从此刻开始获取 last_center_x
        ongoing_list['last_center_x'] = (xmax - xmin) / 2
        Thread(target=detect_last_center_x).start()


def turn_sideServo(work_side):
    side_camera.start()
    flag_list = list(settings.flag_to_servo.keys())

    if work_side == 'left':
        servo_angle = 120
    elif work_side == 'right':
        servo_angle = -60

    CamServo.center()
    time.sleep(1)

    print('turn sideServo')
    CamServo.servocontrol(servo_angle, 30)  # 速度为 30 是合适值

    stdtime = time.time()
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


def start_moving():
    cart.force_steer(15, 0)  # 预热
    time.sleep(0.1)
    ongoing_list['status'] = 'run'
    movingThread = Thread(target=moving, args=())
    if task_lock.locked():
        task_lock.release()
    movingThread.start()
    print('start moving!')


def end_moving():
    ongoing_list['status'] = 'stop'
    task_lock.acquire()
    while task_lock.locked():
        pass
    cart.force_stop()


def calculate_bias(task_name):
    last_center_x = settings.ongoing_list['last_center_x']
    if last_center_x == -1:
        raise Exception('error: last_center_x is an unassigned value!')
    if task_name == 'target':
        posture_range = settings.target_posture_range
    elif task_name == 'camping':
        posture_range = settings.camping_posture_range
    elif task_name == 'fenglangjuxu':
        posture_range = settings.fenglangjuxu_posture_range
    elif task_name == 'soldier':
        posture_range = settings.soldier_posture_range
    elif task_name == 'after_soldier':
        posture_range = settings.after_soldier_posture_range
    else:
        raise Exception("The task_name is incorrect!")

    # 摄像头图片 x 坐标 --> 现实中 x 坐标
    bias_x_cam = last_center_x - 0.5
    coor_x = -bias_x_cam / 0.15 * 7

    # 根据给定的调整范围计算调整值
    if coor_x < posture_range[0]:
        baseline = posture_range[1]
    elif coor_x > posture_range[1]:
        baseline = posture_range[0]
    else:  # 已经在规定范围内，无需调整
        return 0
    bias = baseline - coor_x
    return bias


def adjust_posture(compass_angle, task_name):
    print('adjust posture!')
    compass_angle %= 360

    # 第一次原地旋转校正
    cart.turnToCompassAngle(compass_angle, compass)

    # 左右移动
    bias = calculate_bias(task_name)
    print('task_name = {}, bias = {}'.format(task_name, bias))
    cart.posture_move(bias)

    # 第二次原地旋转校正
    cart.turnToCompassAngle(compass_angle, compass)

    print('adjust posture complete, now angle = {}'.format(compass.read()))


def fortress_move():
    pass


def fortress_task(flag_name, task_name):
    # 往前进以便侧面摄像头看到标志物
    servo_id = settings.flag_to_servo[flag_name]
    flag_servo = servo_flags[servo_id - 1]
    flag_servo.up()
    for i in range(3):
        light.lightgreen()
        time.sleep(2)
        light.lightoff()
        time.sleep(2)
    flag_servo.down()
    ongoing_list[task_name] = 'complete'


def target_task(task_name, direction):
    print('target_task start!')
    time.sleep(0.1)

    if direction == 'forward2backward':
        cart.force_steer(8, 0)
        time.sleep(6)
        cart.force_steer(-8, 0)
    elif direction == 'backward':
        cart.force_steer(-8, 0)
    else:
        raise Exception("direction must in [forward, backward]!")

    diff = [100]

    while True:
        dis_left, dis_right = float(laser_up.read()), float(laser_down.read())
        if not (-1 in [dis_left, dis_right] or dis_left >= 0.2 or dis_right >= 0.2):
            diff.append(abs(dis_right - dis_left))
        str_dis_left = "%.2f" % dis_left
        str_dis_right = "%.2f" % dis_right
        print('dis_left={}, dis_right={}, min_diff={}'.format(str_dis_left, str_dis_right, min(diff)))

        if -1 in [dis_left, dis_right] or dis_left >= 0.2 or dis_right >= 0.2:
            continue
        if abs(dis_left - dis_right) <= 0.05:
            cart.force_stop()
            print('car stop')
            print('dis_left={}, dis_right={}'.format(str_dis_left, str_dis_right))
            break

    time.sleep(0.1)

    print('target servo')
    targetMotor.extent(continue_time=3)

    time.sleep(2)  # DEBUG
    targetMotor.shrink()
    ongoing_list[task_name] = 'complete'


def camping_task():
    cart.force_move([20, 20, 20, 20])
    time.sleep(1.7)
    cart.force_move([-8, -18, -8, -18])
    time.sleep(3.0)
    cart.force_move([-18, -8, -18, -8])
    time.sleep(3.0)
    cart.force_stop()
    cart.turnToCompassAngle(settings.stdCompassAngle + 180, compass)
    cart.force_move([20, 20, 20, 20])
    time.sleep(0.7)
    cart.force_stop()

    # 闪灯
    for i in range(3):
        light.lightred()
        time.sleep(1)
        light.lightoff()
        time.sleep(1)

    cart.force_move([-20, -20, -20, -20])
    time.sleep(0.7)
    cart.force_move([18, 8, 18, 8])
    time.sleep(2.5)
    cart.force_move([18, 18, 18, 18])
    time.sleep(0.6)
    cart.force_move([8, 18, 8, 18])
    time.sleep(2.5)
    cart.force_stop()
    cart.turnToCompassAngle(settings.stdCompassAngle + 180, compass)  # DEBUG, 需要修改
    ongoing_list['camping'] = 'complete'


def fenglangjuxu_task():
    cart.force_move([8, 8, 8, 8])
    print("forward on it")
    while not laser_square.read():
        # print(0)
        pass
    print('laser square ok')
    cart.force_stop()
    print('soldier adjust has been complete!')

    time.sleep(0.5)
    clipServo.loose()
    time.sleep(0.5)
    bottomServo.down()
    time.sleep(0.5)
    clipServo.clamp()
    time.sleep(0.5)
    bottomServo.up()
    time.sleep(0.5)
    ongoing_list['fenglangjuxu'] = 'complete'


def soldier_task():
    cart.force_move([-8, -8, -8, -8])
    print("backward on it")
    while not laser_ball.read():
        # print(1)
        pass
    cart.force_stop()
    print('soldier adjust has been complete!')

    time.sleep(0)
    soldierServo.down()
    time.sleep(1)
    soldierServo.up()

    ongoing_list['soldier'] = 'complete'


def test_target():
    target_task(task_name='target1', direction='forward2backward')


def test_compass_move():
    stdCompassAngle = compass.read()
    cart.turnToCompassAngle(stdCompassAngle, compass)


if __name__ == '__main__':
    test_compass_move()
    pass
