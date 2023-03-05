import ctypes
from sdl2 import *


class Joystick:
    def __init__(self, app: any, index: int) -> None:
        self.destroyed = True
        self.index = index
        try:
            self.player_index = SDL_JoystickGetDevicePlayerIndex(index)
        except NameError:
            self.player_index = -1
        self.name = app.bts(SDL_JoystickNameForIndex(index))
        try:
            self.path = app.bts(SDL_JoystickPathForIndex(index))
        except NameError:
            self.path = ''
        self.guid = SDL_JoystickGetDeviceGUID(index)
        try:
            self.vendor = SDL_JoystickGetDeviceVendor(index)
            self.product = SDL_JoystickGetDeviceProduct(index)
            self.product_version = SDL_JoystickGetDeviceProductVersion(index)
        except NameError:
            self.path = 0
        self.type = {
            SDL_JOYSTICK_TYPE_UNKNOWN: 'unknown',
            SDL_JOYSTICK_TYPE_GAMECONTROLLER: 'game_controller',
            SDL_JOYSTICK_TYPE_WHEEL: 'wheel',
            SDL_JOYSTICK_TYPE_ARCADE_STICK: 'arcade_stick',
            SDL_JOYSTICK_TYPE_FLIGHT_STICK: 'flight_stick',
            SDL_JOYSTICK_TYPE_DANCE_PAD: 'dance_pad',
            SDL_JOYSTICK_TYPE_GUITAR: 'guitar',
            SDL_JOYSTICK_TYPE_DRUM_KIT: 'drum_kit',
            SDL_JOYSTICK_TYPE_ARCADE_PAD: 'arcade_pad',
            SDL_JOYSTICK_TYPE_THROTTLE: 'throttle'
        }.get(SDL_JoystickGetDeviceType(index))
        self.hat_map = {
            SDL_HAT_CENTERED: 'centered',
            SDL_HAT_DOWN: 'down',
            SDL_HAT_LEFT: 'left',
            SDL_HAT_LEFTDOWN: 'left_down',
            SDL_HAT_LEFTUP: 'left_up',
            SDL_HAT_RIGHT: 'right',
            SDL_HAT_RIGHTDOWN: 'right_down',
            SDL_HAT_RIGHTUP: 'right_up',
            SDL_HAT_UP: 'up'
        }
        self.power_map = {
            SDL_JOYSTICK_POWER_UNKNOWN: 'unknown',
            SDL_JOYSTICK_POWER_EMPTY: 'empty',
            SDL_JOYSTICK_POWER_LOW: 'low',
            SDL_JOYSTICK_POWER_MEDIUM: 'medium',
            SDL_JOYSTICK_POWER_FULL: 'full',
            SDL_JOYSTICK_POWER_WIRED: 'wired',
            SDL_JOYSTICK_POWER_MAX: 'max'
        }
        self.firmware_version = 0
        self.serial = b''
        self.instance_id = SDL_JoystickGetDeviceInstanceID(index)
        self.joystick = SDL_Joystick(index)
        self.opened = False
        self.num_axes = 0
        self.num_balls = 0
        self.num_hats = 0
        self.num_buttons = 0
        self.has_led = False
        self.has_rumble = False
        self.has_rumble_triggers = False
        self.destroyed = False
        # TODO:
        #  GUID functions
        #  Virtual Joysticks if needed (it's for you, I'm lazy!!!!!!!!!!!)

    def send_effect(self, data: bytes) -> None:
        SDL_JoystickSendEffect(self.joystick, data, len(data))

    def set_led(self, color: any) -> None:
        SDL_JoystickSetLED(self.joystick, int(color[0]), int(color[1]), int(color[2]))

    def rumble(self, low_freq_rumble: int, high_freq_rumble: int, duration: float) -> None:
        SDL_JoystickRumble(self.joystick, low_freq_rumble, high_freq_rumble, int(duration * 1000))

    def rumble_triggers(self, low_freq_rumble: int, high_freq_rumble: int, duration: float) -> None:
        SDL_JoystickRumbleTriggers(self.joystick, low_freq_rumble, high_freq_rumble, int(duration * 1000))

    def update_info(self) -> None:
        self.opened = True
        self.num_axes = SDL_JoystickNumAxes(self.joystick)
        self.num_balls = SDL_JoystickNumBalls(self.joystick)
        self.num_hats = SDL_JoystickNumHats(self.joystick)
        self.num_buttons = SDL_JoystickNumButtons(self.joystick)
        try:
            self.has_led = bool(SDL_JoystickHasLED(self.joystick))
            self.has_rumble = bool(SDL_JoystickHasRumble(self.joystick))
            self.has_rumble_triggers = bool(SDL_JoystickHasRumbleTriggers(self.joystick))
        except NameError:
            pass
        try:
            self.firmware_version = SDL_JoystickGetFirmwareVersion(self.joystick)
            self.serial = SDL_JoystickGetSerial(self.joystick) or b''
        except NameError:
            return

    def get_power_level(self) -> str:
        return self.power_map[SDL_JoystickCurrentPowerLevel(self.joystick)]

    def get_button(self, button: int) -> bool:
        return bool(SDL_JoystickGetButton(self.joystick, button))

    def get_ball(self, ball: int) -> tuple:
        x_ptr, y_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_JoystickGetBall(self.joystick, ball, x_ptr, y_ptr)
        return x_ptr.value, y_ptr.value

    def get_hat(self, hat: int) -> str:
        return self.hat_map[SDL_JoystickGetHat(self.joystick, hat)]

    def get_axis_initial_state(self, axis: int) -> any:
        state_ptr = ctypes.c_int16()
        return SDL_JoystickGetAxisInitialState(self.joystick, axis, state_ptr) and state_ptr.value

    def get_axis(self, axis: int) -> int:
        return SDL_JoystickGetAxis(self.joystick, axis)

    def is_attached(self) -> bool:
        return bool(SDL_JoystickGetAttached(self.joystick))

    def open(self) -> None:
        self.joystick = SDL_JoystickOpen(self.index)
        self.update_info()

    def open_from_instance_id(self) -> None:
        self.joystick = SDL_JoystickFromInstanceID(self.instance_id)
        self.update_info()

    def open_from_player_index(self) -> None:
        self.joystick = SDL_JoystickFromPlayerIndex(self.player_index)
        self.update_info()

    def set_player_index(self, player_index: int = -1) -> None:
        self.player_index = player_index
        SDL_JoystickSetPlayerIndex(self.joystick, player_index)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        if self.opened:
            self.opened = False
            SDL_JoystickClose(self.joystick)
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
