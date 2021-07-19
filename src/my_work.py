# 若不连接 WOBOT 控制器，则注释以下内容
#%%
from serial_port import serial_connection
from widgets import Light, Servo, Motor_rotate, Buzzer, Servo_pwm, UltrasonicSensor, Button
from cart import Cart

serial = serial_connection
from joystick import JoyStick
from camera import Camera
import cv2
import time
import threading
import numpy as np


def test_light(light_port, color):
    light = Light(light_port)
    red = [80, 0, 0]
    green = [0, 80, 0]
    yellow = [80, 80, 0]
    off = [0, 0, 0]
    light_color = [0, 0, 0]
    if color == 'red':
        light_color = red
    elif color == 'green':
        light_color = green
    elif color == 'yellow':
        light_color = yellow
    elif color == 'off':
        light_color = off
    light.lightcontrol(0, light_color[0], light_color[1], light_color[2])


def test_motor(port=1, speed=50):
    ports = list(port)
    for port in ports:
        exec('motor_{} = Motor_rotate({})'.format(port, port))
    while True:
        for port in ports:
            exec('motor_{}.motor_rotate({})'.format(port, speed))


def test_servo(ID=1):
    servo = Servo(ID)
    while True:
        servo.servocontrol(-60, 50)
        time.sleep(0.5)
        servo.servocontrol(60, 50)
        time.sleep(0.5)


def test_joystick():
    js = JoyStick()
    js.open()
    while True:
        time, value, type_, number = js.read()
        print('-' * 32)
        print('time = {}'.format(time))
        print('value = {}'.format(value))
        print('type_ = {}'.format(type_))
        print('number = {}'.format(number))
        print('x_axis = {}'.format(js.get_x_axis()))


def test_img_cruiseModel():
    cruiser = Cruiser()
    img = cv2.imread('test/cruise/7.png')
    # print(img.shape)
    print('angle = {}'.format(cruiser.cruise(img)))


def test_cam_cruiseModel():
    cruiser = Cruiser()
    front_camera = Camera(front_cam, [640, 480])
    front_camera.start()

    while True:
        front_image = front_camera.read()
        cv2.imwrite('front_image.jpg', front_image)
        print('angle = {}'.format(cruiser.cruise(front_image)))


def test_sign():
    cruiser = Cruiser()
    front_camera = Camera(front_cam, [640, 480])
    front_camera.start()

    while True:
        front_image = front_camera.read()
        cv2.imwrite('front_image.jpg', front_image)


def test_cart():
    cart = Cart()
    while True:
        # cart.steer(angle=-2)
        # time.sleep(1)
        cart.move([40, 40, 40, 40])
        time.sleep(1)
        cart.move([0, 0, 0, 0])
        time.sleep(1)
        # cart.move([80, 80, 80, 80])


def test_thread():
    while True:
        print('open thread')


def joystick_thread(js, cart):
    while True:
        time, value, type_, number = js.read()
        # Key = X | speed = 80
        if type_ == 1 and number == 3 and value == 1:
            cart.speed = 50
            print('Key[X] down, run at {}'.format(cart.speed))

        # Key = B | stop | keep the value of angle
        if type_ == 1 and number == 1 and value == 1:
            cart.speed = 0
            print('Key[B] down, stop')

        # Key = Y | angle = 0
        if type_ == 1 and number == 4 and value == 1:
            cart.angle = 0
            print('Key[Y] down, angle = 0')

        # Key = LEFT | angle -= 0.25
        if type_ == 2 and number == 6 and value == -32767:
            if cart.angle == -2.0:
                print('Key[LEFT] down, angle == -2.0, maximizing')
            else:
                cart.angle -= 0.25
                print('Key[LEFT] down, angle -= 0.25, now angle = {}'.format(cart.angle))

        # Key = RIGHT | angle += 0.25
        if type_ == 2 and number == 6 and value == 32767:
            if cart.angle == 2.0:
                print('Key[RIGHT] down, angle == 2.0, maximizing')
            else:
                cart.angle += 0.25
                print('Key[RIGHT] down, angle += 0.25, now angle = {}'.format(cart.angle))


def test_joystick_run():
    # init
    js = JoyStick()
    js.open()
    cart = Cart()
    cart.angle = 0
    cart.velocity = 0
    js_thread = threading.Thread(target=joystick_thread, args=(js, cart,))
    js_thread.start()
    print('Init complete, wait for instruction')

    while True:
        cart.steer(cart.velocity, cart.angle)

    js_thread.join()
    cart.stop()


def test_buzzer():
    buzzer = Buzzer()
    buzzer.rings()


def test_servo_pwm():
    servo_pwm = Servo_pwm(4)
    while True:
        servo_pwm.servocontrol(30, 100)
        servo_pwm.servocontrol(0, 100)
        servo_pwm.servocontrol(120, 100)


def test_ultrasonicSensor():
    ultra = UltrasonicSensor(1)
    while True:
        print(ultra.read())


def test_button():
    button = Button(1, 'RIGHT')
    ultra = UltrasonicSensor(2)
    while True:
        if button.clicked():
            print(ultra.read())


def test_preprocess(src):
    img = cv2.resize(src, (608, 608))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img /= 255
    img -= [0.485, 0.456, 0.406]
    img /= [0.229, 0.224, 0.225]

    z = np.zeros((1, 608, 608, 3)).astype(np.float32)
    z[0, 0:img.shape[0], 0:img.shape[1] + 0, 0:img.shape[2]] = img
    z = z.reshape(1, 3, 608, 608)
    return z


def test_mark():
    pass


def test_work():
    from marker import init_predictor, getResult
    from threading import Thread
    predictor = init_predictor(model_dir=settings.taskModelPath)
    sideCamera = Camera(src=1)
    sideServo = Servo(1)
    sideServo.servocontrol(30, 50)  # 转到中心
    time.sleep(2)

    sideServo.servocontrol(-60, 25)

    while True:
        side_image = sideCamera.read()
        result = getResult(side_image, predictor=predictor, mode='task')
        if result:
            print(result)


def test_target():
    from laser import Laser
    from widgets import SideMotor
    targetMotor = SideMotor(8)
    targetMotor.shrink()
    laser_left = Laser(port=2)
    laser_right = Laser(port=1)
    cart = Cart()
    cart.steer(8, 0)
    time.sleep(0.1)

    while True:
        dis_left, dis_right = float(laser_left.read()), float(laser_right.read())
        str_dis_left = "%.2f" % dis_left
        str_dis_right = "%.2f" % dis_right
        print('dis_left={}, dis_right={}'.format(str_dis_left, str_dis_right))
        # continue
        if -1 in [dis_left, dis_right] or dis_left >= 0.5 or dis_right >= 0.5:
            continue
        if abs(dis_left - dis_right) <= 0.04:
            cart.stop()
            print('car stop')
            print('dis_left={}, dis_right={}'.format(str_dis_left, str_dis_right))
            break
    laser_left.stop()
    laser_right.stop()
    time.sleep(0.1)

    test_target_servo(targetMotor)


def test_target_servo(targetMotor=None):
    from widgets import SideMotor
    if targetMotor is None:
        targetMotor = SideMotor(8)
    print('target servo')
    while True:
        targetMotor.extent(continue_time=3)
        targetMotor.shrink()


def test_run():
    cart = Cart()
    cart.move([15, 3, 15, 3])
    time.sleep(1)


def test_camping():
    from cart import Cart
    cart = Cart()
    # cart.force_move([0, -20, 0, -20])
    # cart.stop()
    # return

    cart.force_move([20, 20, 20, 20])
    time.sleep(2.2)
    cart.force_move([-8, -18, -8, -18])
    time.sleep(3.0)
    cart.force_move([-18, -8, -18, -8])
    time.sleep(3.0)

    cart.stop()
    time.sleep(2)

    cart.force_move([18, 8, 18, 8])
    time.sleep(2.8)
    cart.force_move([18, 18, 18, 18])
    time.sleep(0.6)
    cart.force_move([8, 18, 8, 18])
    time.sleep(2.8)

    cart.stop()


def test_posture(distance=5):
    basespeed = 15
    speed_ratio = 0.4

    if distance < 2:
        speed_ratio = 0.2
        drivetime = distance * 0.95
    elif distance < 4:
        speed_ratio = 0.15
        drivetime = distance * 0.75
    else:
        speed_ratio = -0.05
        drivetime = distance * 0.25
    l_speed = basespeed
    r_speed = basespeed * speed_ratio
    print('l_speed = {}, r_speed = {}'.format(l_speed, r_speed))
    cart.move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)

    cart.stop()  # DEBUG

    l_speed = basespeed * speed_ratio
    r_speed = basespeed
    print('l_speed = {}, r_speed = {}'.format(l_speed, r_speed))
    cart.move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)
    l_speed = r_speed = -basespeed
    cart.move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)
    cart.stop()


def test_cam():
    from camera import Camera
    from cruiser import img_process
    front_camera = Camera()

    img = front_camera.read()
    _, mask = img_process(img)
    cv2.imwrite('test_hsv_img.png', mask)
    print('save img')


def test_fenglangjuxu():
    from widgets import SideMotor, Servo_pwm
    targetMotor = SideMotor(8)
    clampServo = Servo_pwm(9)
    bottomServo = Servo(2)
    bottomServo.servocontrol(0, 30)
    pass

    # while True:
    #     print('work successfully!')
    #     clampServo.servocontrol(angle=0, speed=30)
    #     time.sleep(1)
    #     clampServo.servocontrol(angle=60, speed=30)
    #     time.sleep(1)

    # targetMotor.extent()


def test_soldier():
    from widgets import Servo_pwm
    soldierServo = Servo_pwm(8)
    soldierServo.servocontrol(0, 30)


def test_compass():
    from compass import Compass
    compass = Compass(1)
    while True:
        print(compass.read())


def detect_dis():
    from camera import Camera
    from marker import getResult, init_predictor
    import settings

    front_camera = Camera()
    sign_predictor = init_predictor(settings.signModelPath)

    while True:
        front_image = front_camera.read()
        signResult = getResult(front_image, sign_predictor, mode='sign')
        if signResult:
            xmin, xmax = signResult[0][2][0], signResult[0][2][2]
            print("center = {}".format((xmin + xmax) / 2))


def test_pos_move(drivetime=3):
    l_speed = -15
    r_speed = 0
    cart.force_move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)

    l_speed = 0
    r_speed = -15
    cart.force_move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)

    l_speed = r_speed = 15
    cart.force_move([l_speed, r_speed, l_speed, r_speed])
    time.sleep(drivetime)

    cart.force_stop()


def test_target_move():
    # 通过摄像头获取中心点
    from camera import Camera
    from marker import getResult, init_predictor
    import settings

    front_camera = Camera()
    sign_predictor = init_predictor(settings.signModelPath)

    front_image = front_camera.read()
    signResult = getResult(front_image, sign_predictor, mode='sign')
    xmin, xmax = signResult[0][2][0], signResult[0][2][2]
    bias_x_cam = (xmin + xmax) / 2 - 0.5
    coor_x = -bias_x_cam / 0.15 * 7
    print(coor_x)

    target_x = -1.25
    bias = target_x - coor_x
    test_posture(bias)


def test_run_algo_posture_move():
    from run_algo import posture_move
    posture_move(-3)


def test_turn_in_circles():
    from cart import Cart
    from compass import Compass
    cart = Cart()
    compass = Compass(port=3)
    time.sleep(1)  # 初始化
    if abs(compass.read() - 17) >= 4:  # 倒放352
        cart.force_move([15, -15, 15, -15])
    while abs(compass.read() - 17) >= 7:
        pass
    cart.force_stop()
    print(compass.read())


if __name__ == '__main__':
    import settings

    # cart = Cart()

    # test_light(2, 'off')
    # test_motor(port=[1, 2, 3, 4], speed=-20)
    # test_joystick()
    # test_cam_cruiseModel()
    # test_cart()
    # test_img_cruiseModel()
    # test_joystick_run()
    # test_buzzer()
    # test_servo(2)
    # test_servo_pwm()
    # test_ultrasonicSensor()
    # test_button()
    # test_mark()
    # test_work()
    # test_target()
    # test_run()
    # test_target_servo()
    test_camping()
    # test_posture(1)
    # test_fenglangjuxu()
    # test_soldier()
    # test_compass()
    # test_target_move()
    # test_pos_move(0.8)
    # test_run_algo_posture_move()
    # test_turn_in_circles()

    print('my work')
    pass
