from widgets import Servo, Servo_pwm,Motor_rotate, Magneto_sensor,UltrasonicSensor,Light,Buzzer
from widgets import *
from driver import Driver, SLOW_DOWN_RATE
import time
import cart
#升旗任务
def raiseflag(motor_port,magsensor_port):
    print("raiseflag start!")
    setmotor1 = Motor_rotate(motor_port)
    magsensor=Magneto_sensor(magsensor_port)
    setmotor1.motor_rotate(17)
    # time.sleep(0.1)
    while True:
        if magsensor.read()!=None:
            ma=magsensor.read()
        else:
            ma=0
        print("ma=",ma)
        if ma>90:
            setmotor1.motor_rotate(0)
            time.sleep(1)
            # setmotor1.motor_rotate(17)
            # time.sleep(0.1)
            break
    for i in range(0,3):
        Lightwork(2, "green")
        time.sleep(0.05)
        Lightwork(2, "off")
        time.sleep(0.05)
    setmotor1.motor_rotate(17)
    time.sleep(0.18)
    setmotor1.motor_rotate(0)
    time.sleep(0.1)
    print("raiseflag stop!")
#激战任务
def shot_target(motor_port):
    print("shot_target start!")
    setmotor1 = Motor_rotate(motor_port)
    time.sleep(0.5)
    for i in range(0,2):
        setmotor1.motor_rotate(-60)
        time.sleep(1.2)
        setmotor1.motor_rotate(0)
        time.sleep(0.2)
        setmotor1.motor_rotate(40)
        time.sleep(0.8)
        setmotor1.motor_rotate(0)
        time.sleep(0.1)
    print("shot_target stop!")
#缴获战利品
def capture_target(servo485ID,servoPWMID):
    servo1=Servo(servo485ID)
    servo2=Servo_pwm(servoPWMID)
    servo1speed=100
    servo2speed=50
    # servo1.servocontrol(-85,servo1speed)
    time.sleep(1)
    servo2.servocontrol(160, servo2speed)
    time.sleep(2)
    servo1.servocontrol(30, 60)
    time.sleep(2)
    servo2.servocontrol(85, servo2speed)
    time.sleep(2)
    servo1.servocontrol(-85,servo1speed)
    time.sleep(2)
#运送粮草
def banyun(motor_port):
    print("banyun start!")
    setmotor1 = Motor_rotate(motor_port)
    time.sleep(0.5)
    setmotor1.motor_rotate(-8)
    time.sleep(1)
    setmotor1.motor_rotate(0)
    time.sleep(0.2)
    setmotor1.motor_rotate(10)
    time.sleep(0.8)
    setmotor1.motor_rotate(0)
    time.sleep(0.1)
    print("banyun stop!")
#灯光
def Lightwork(light_port,color):
    light=Light(light_port)
    red=[80,0,0]
    green=[0,80,0]
    yellow=[80,80,0]
    off=[0,0,0]
    light_color=[0,0,0]
    if color =='red':
        light_color=red
    elif color=='green':
        light_color=green
    elif color=='yellow':
        light_color=yellow
    elif color=='off':
        light_color = off
    light.lightcontrol(0,light_color[0],light_color[1],light_color[2])
#宿营
def take_barracks():
    driver = Driver()
    driver.set_speed(driver.full_speed)
    driver.set_Kx(0.8)
    driver.stop()
    time.sleep(0.5)
    driver.driver_run(20, 19)
    time.sleep(3.4)
    driver.driver_run(-8, -18)
    time.sleep(3.4)
    driver.driver_run(-18, -8)
    time.sleep(3.0)
    driver.stop()
    for i in range(0, 4):
        Lightwork(2, "red")
        time.sleep(0.2)
        Lightwork(2, "off")
    driver.driver_run(18, 8)
    time.sleep(2.8)
    driver.driver_run(18, 18)
    time.sleep(0.6)
    driver.driver_run(8, 18)
    time.sleep(2.8)
    driver.stop()
#鸣笛
def buzzer():
    buzzer=Buzzer()
    for i in range(1,10):
        # print(i)
        buzzer.rings()
        time.sleep(0.5)

# from thserial import Recv_threading
if __name__ == '__main__':
    # servo1 = Servo(3)
    # servo2 = Servo_pwm(2)
    # mk =Recv_threading()
    # mk.start_port()
    # capture_target(3,2)
    # mk.stop()
    # mk.th.join()
    # raiseflag(4,3)
    banyun(1)