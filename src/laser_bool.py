import serial

import settings


class LaserBool:
    def __init__(self, port):
        portx = "/dev/" + str(port)
        bps = 115200
        self.serial = serial.Serial(portx,
                                    int(bps),
                                    timeout=0.01,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    xonxoff=False,
                                    rtscts=False,
                                    dsrdtr=False,
                                    writeTimeout=0.1)

        try:
            self.serial.open()
        except Exception as e:
            if not str(e) == 'Port is already open.':
                raise Exception("error open serial port: " + str(e))

    def read(self):
        self.serial.flushInput()
        self.serial.flushOutput()
        response = self.serial.readline()
        try:
            if response.decode('utf-8'):
                return 1
            else:
                return 0
        except:
            return False


if __name__ == '__main__':
    laser_square = LaserBool(port=settings.laser_square_port)
    laser_ball = LaserBool(port=settings.laser_ball_port)
    # print(laser_bool_left.read())
    while True:
        if laser_square.read() == 1:
            print('laser_square')
        if laser_ball.read() == 1:
            print('laser_ball')
