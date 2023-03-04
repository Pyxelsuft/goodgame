from sdl2 import *


class Finger:
    def __init__(self, finger: SDL_Finger) -> None:
        self.id = finger.id
        self.x, self.y = finger.x, finger.y
        self.pressure = finger.pressure


class TouchDevice:
    def __init__(self, app: any, index: int) -> None:
        self.index = index
        self.id = SDL_GetTouchDevice(index)
        try:
            self.name = app.bts(SDL_GetTouchName(index))
        except NameError:
            self.name = ''
        try:
            tp = SDL_GetTouchDeviceType(self.id)
            if tp == SDL_TOUCH_DEVICE_DIRECT:
                self.type = 'direct'
            elif SDL_TOUCH_DEVICE_INDIRECT_ABSOLUTE:
                self.type = 'indirect_absolute'
            elif SDL_TOUCH_DEVICE_INDIRECT_RELATIVE:
                self.type = 'indirect_relative'
            else:
                self.type = 'invalid'
        except NameError:
            self.type = 'unknown'
        self.num_fingers = SDL_GetNumTouchFingers(self.id)

    def get_finger(self, finger_id: int) -> Finger:
        return Finger(SDL_GetTouchFinger(self.id, finger_id))

    def get_all_fingers(self) -> tuple:
        return tuple(self.get_finger(_x) for _x in range(self.num_fingers))
