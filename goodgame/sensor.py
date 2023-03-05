import ctypes
from sdl2 import *


class Sensor:
    def __init__(self, app: any, index: int) -> None:
        self.destroyed = True
        self.index = index
        self.name = app.bts(SDL_SensorGetDeviceName(index))
        self.type = {
            SDL_SENSOR_INVALID: 'invalid',
            SDL_SENSOR_UNKNOWN: 'unknown',
            SDL_SENSOR_ACCEL: 'accel',
            SDL_SENSOR_GYRO: 'gyro',
            SDL_SENSOR_ACCEL_L: 'accel_l',
            SDL_SENSOR_GYRO_L: 'gyro_l',
            SDL_SENSOR_ACCEL_R: 'accel_r',
            SDL_SENSOR_GYRO_R: 'gyro_r'
        }.get(SDL_SensorGetDeviceType(index))
        self.non_portable_type = SDL_SensorGetDeviceNonPortableType(index)
        self.instance_id = SDL_SensorGetDeviceInstanceID(index)
        self.sensor = SDL_Sensor()
        self.opened = False
        self.destroyed = False

    def get_data(self, num_values: int) -> tuple:
        data_ptr = (ctypes.c_float * num_values)()
        SDL_SensorGetData(self.sensor, data_ptr, num_values)
        return tuple(data_ptr[_x] for _x in range(num_values))

    def open_from_instance_id(self) -> None:
        self.opened = True
        self.sensor = SDL_SensorFromInstanceID(self.instance_id)

    def open(self) -> None:
        self.opened = True
        self.sensor = SDL_SensorOpen(self.index)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        if self.opened:
            self.opened = False
            SDL_SensorClose(self.sensor)
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
