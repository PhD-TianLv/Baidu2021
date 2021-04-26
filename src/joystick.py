import os
import struct


class JoyStick:
    """
    Key[A]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 0
    Key[B]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 1
    Key[X]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 3
    Key[Y]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 4
    Key[LEFT]:
        value[key_down]: -32767 | value[key_up]: 0
        type_: 2
        number: 6
    Key[RIGHT]:
        value[key_down]: 32767 | value[key_up]: 0
        type_: 2
        number: 6
    Key[UP]:
        value[key_down]: -32767 | value[key_up]: 0
        type_: 2
        number: 7
    Key[DOWN]:
        value[key_down]: 32767 | value[key_up]: 0
        type_: 2
        number: 7
    Key[L1]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 6
    Key[R1]:
        value[key_down]: 1 | value[key_up]: 0
        type_: 1
        number: 7
    Key[L2] | Key[R2]:
        Unknown | Difficult | Not recommended
    Axis[LEFT] | Axis[RIGHT]:
        Unknown | Difficult | Not recommended
    """

    def __init__(self):
        print('avaliable devices: ', end='')
        for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                print('/dev/input/%s' % fn)

        self.fn = '/dev/input/js0'
        self.x_axis = 0
        self.jsdev = open(self.fn, 'rb')
        self.evbuf = self.jsdev.read(8)

    def read(self):
        self.evbuf = self.jsdev.read(8)
        return struct.unpack('IhBB', self.evbuf)

    def type(self, type_):
        if type_ & 0x01:
            return "button"
        if type_ & 0x02:
            return "axis"

    def button_state(self):
        return 1

    def get_x_axis(self):
        time, value, type_, number = struct.unpack('IhBB', self.evbuf)
        if number == 1:
            fvalue = value / 32767
            return fvalue

    def get_key(self) -> list:
        """
        获取所有已按下的按键列表
        :return: 所有已按下按键的列表
        """
        time, value, type_, number = self.read()
        keys = []
        if type_ == 1 and number == 0 and value == 1:
            keys.append('A')
        if type_ == 1 and number == 1 and value == 1:
            keys.append('B')
        if type_ == 1 and number == 3 and value == 1:
            keys.apppend('X')
        if type_ == 1 and number == 4 and value == 1:
            keys.apppend('Y')
        if type_ == 2 and number == 6 and value == -32767:
            keys.apppend('LEFT')
        if type_ == 2 and number == 6 and value == 32767:
            keys.apppend('RIGHT')
        if type_ == 2 and number == 7 and value == -32767:
            keys.apppend('UP')
        if type_ == 2 and number == 7 and value == 32767:
            keys.apppend('DOWN')
        if type_ == 1 and number == 6 and value == 1:
            keys.apppend('L1')
        if type_ == 1 and number == 7 and value == 1:
            keys.apppend('R1')
        return keys