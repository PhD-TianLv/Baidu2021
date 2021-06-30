from marker import getResult as getMark, init_predictor as init_mark_predictor
import settings
from camera import Camera
from widgets import Servo

task_predictor = init_mark_predictor(settings.taskModelPath)
side_camera = Camera(src=1, autoStart=False)
sideServo = Servo(1)
sideServo.servocontrol(-60, 50)

while True:
    side_image = side_camera.read()
    taskResult = getMark(side_image, task_predictor, mode='task')
