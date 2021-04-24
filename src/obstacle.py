from widgets import Servo, Servo_pwm, Motor_rotate, Magneto_sensor, UltrasonicSensor, Light, Buzzer
from widgets import *
import time
import old_cart


def Lightwork(light_port, color):
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


# from thserial import Recv_threading
if __name__ == '__main__':
    pass
    # servo1 = Servo(3)
    # servo2 = Servo_pwm(2)
    # mk = Recv_threading()
    # mk.start_port()
    # capture_target(3,2)
    # mk.stop()
    # mk.th.join()
    # raiseflag(4,3)
    # num=0
    # while True:
    #     num+=1
    #     print("num=",num)
    #     servo1speed = 100
    #     servo2speed = 30
    #     Lightwork(2, "red")
    #     servo1.servocontrol(-85, servo1speed)
    #     # time.sleep(2)
    #     # servo2.servocontrol(70, servo2speed)
    #     time.sleep(2)
    #     Lightwork(2, "green")
    #     servo1.servocontrol(5, servo1speed)
    #     # time.sleep(2)
    #     # servo2.servocontrol(40, servo2speed)
    #     time.sleep(2)
    # buzzer()
    # shot_target(2)
    # raiseflag(4)
    # capture_target(2,2)
    # temperature_control(2)
    # while True:
    #     Lightwork(2, "yellow")
    #     Lightwork(4, "yellow")
    #     time.sleep(1)
    #     Lightwork(2, "red")
    #     Lightwork(4, "red")
    #     time.sleep(1)
    #     Lightwork(2, "green")
    #     Lightwork(4, "green")
    #     time.sleep(1)
    #     Lightwork(2, "off")
    #     Lightwork(4, "off")
    #     time.sleep(1)
    # time.sleep(1)
    # print("Start work!")
    # getfriut(1)
    # time.sleep(2)
    # takepackage(1)
    # print("End!")
