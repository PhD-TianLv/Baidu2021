import serial
import settings

from threading import Lock


class Serial:
    def __init__(self):
        portx = "/dev/" + str(settings.wobot_port)
        print('wobot_port = {}'.format(portx))
        bps = 115200
        self.res = None
        self.serial = serial.Serial(portx,
                                    int(bps),
                                    timeout=0.01,
                                    parity=serial.PARITY_NONE,
                                    stopbits=1,
                                    writeTimeout=0)

    def write(self, data):
        lock = Lock()
        lock.acquire()
        try:
            self.serial.write(data)
            self.serial.flush()
            self.res = self.serial.readline()
        finally:
            lock.release()

    def read(self):
        return self.res


serial_connection = Serial()
