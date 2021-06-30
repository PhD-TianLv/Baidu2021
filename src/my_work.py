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
    servo_pwm = Servo_pwm(5)
    while True:
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
    import settings
    from marker import init_predictor, ssd_preprocess, infer_ssd, analyse_res

    predictor = init_predictor(model_dir=settings.markModelPath)
    img_path = 'test_imgs/changqiezi_191.jpg'
    img = cv2.imread(img_path)

    data = test_preprocess(img)
    res = infer_ssd(predictor, img, data)
    result = analyse_res(res, debug=True)
    print('result = {}'.format(result))


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
    laser_left = Laser(port=2)
    laser_right = Laser(port=1)
    cart = Cart()
    cart.steer(8, 0)

    while True:
        dis_left, dis_right = float(laser_left.read()), float(laser_right.read())
        str_dis_left = "%.2f" % dis_left
        str_dis_right = "%.2f" % dis_right
        print('dis_left={}, dis_right={}'.format(str_dis_left, str_dis_right))
        if -1 in [dis_left, dis_right] or dis_left >= 0.5 or dis_right >= 0.5:
            continue
        if abs(dis_left - dis_right) <= 0.04:
            cart.stop()
            print('car stop')
            break


def test_run():
    cart = Cart()
    cart.steer(10, 0)


if __name__ == '__main__':
    import settings

    # test_light(2, 'off')
    # test_motor(port=[1, 2, 3, 4], speed=-20)
    # test_joystick()
    # test_cam_cruiseModel()
    # test_cart()
    # test_img_cruiseModel()
    # test_joystick_run()
    # test_buzzer()
    # test_servo(1)
    # test_servo_pwm()
    # test_ultrasonicSensor()
    # test_button()
    # test_mark()
    # test_work()
    test_target()
    # test_run()
    pass
