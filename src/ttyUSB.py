from compass_prepare import Compass
from laser import Laser
from laser_bool import LaserBool
import settings
import time


def distribute_port():
    flags = {
        'compass': 0
    }
    for port in range(0, 10):
        try:
            compass = Compass(port, init_flag=False)
            if compass.distribute_port():
                settings.compass_port = port
                print('compass port = {}'.format(port))
                flags['compass'] = 1
        except:
            pass
    if not flags['compass']:
        raise Exception("cannot find compass port!")


if __name__ == '__main__':
    distribute_port()
