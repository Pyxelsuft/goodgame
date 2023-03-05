from sdl2 import *
from .video import Display

try:
    SDL_TOUCH_MOUSEID = SDL_TOUCH_MOUSEID
except NameError:
    SDL_TOUCH_MOUSEID = 2 ** 32 - 1

default_window_id = [1]


class CommonEvent:
    def __init__(self, event: SDL_Event) -> None:
        self.event = event
        self.timestamp = event.timestamp
        self.type = event.type


class QuitEvent(CommonEvent):
    pass


class JoyAxisEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.axis = event.axis
        self.value = event.value


class JoyBallEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.ball = event.ball
        self.rel = (event.xrel, event.yrel)


class JoyButtonEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.button = event.button
        self.state = 'pressed' if event.state == SDL_PRESSED else 'released'


class JoyBatteryEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.button = event.button
        self.level = {
            SDL_JOYSTICK_POWER_UNKNOWN: 'unknown',
            SDL_JOYSTICK_POWER_EMPTY: 'empty',
            SDL_JOYSTICK_POWER_LOW: 'low',
            SDL_JOYSTICK_POWER_MEDIUM: 'medium',
            SDL_JOYSTICK_POWER_FULL: 'full',
            SDL_JOYSTICK_POWER_WIRED: 'wired',
            SDL_JOYSTICK_POWER_MAX: 'max'
        }.get(event.level)


class JoyDeviceEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        if self.type == SDL_JOYDEVICEADDED:
            self.index = event.which
            self.instance_id = 0
        else:
            self.index = 0
            self.instance_id = event.which


class JoyHatEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.hat = event.hat
        self.state = {
            SDL_JOYSTICK_POWER_UNKNOWN: 'unknown',
            SDL_JOYSTICK_POWER_EMPTY: 'empty',
            SDL_JOYSTICK_POWER_LOW: 'low',
            SDL_JOYSTICK_POWER_MEDIUM: 'medium',
            SDL_JOYSTICK_POWER_FULL: 'full',
            SDL_JOYSTICK_POWER_WIRED: 'wired',
            SDL_JOYSTICK_POWER_MAX: 'max'
        }.get(event.value)


class ControllerAxisEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.axis = {
            SDL_CONTROLLER_AXIS_INVALID: 'invalid',
            SDL_CONTROLLER_AXIS_LEFTX: 'left_x',
            SDL_CONTROLLER_AXIS_LEFTY: 'left_y',
            SDL_CONTROLLER_AXIS_RIGHTX: 'right_x',
            SDL_CONTROLLER_AXIS_RIGHTY: 'right_y',
            SDL_CONTROLLER_AXIS_TRIGGERLEFT: 'trigger_left',
            SDL_CONTROLLER_AXIS_TRIGGERRIGHT: 'trigger_right',
            SDL_CONTROLLER_AXIS_MAX: 'max'
        }.get(event.axis)
        self.value = event.value


class ControllerButtonEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.button = {
            SDL_CONTROLLER_BUTTON_INVALID: 'invalid',
            SDL_CONTROLLER_BUTTON_A: 'a',
            SDL_CONTROLLER_BUTTON_B: 'b',
            SDL_CONTROLLER_BUTTON_X: 'x',
            SDL_CONTROLLER_BUTTON_Y: 'y',
            SDL_CONTROLLER_BUTTON_BACK: 'back',
            SDL_CONTROLLER_BUTTON_GUIDE: 'guide',
            SDL_CONTROLLER_BUTTON_START: 'start',
            SDL_CONTROLLER_BUTTON_LEFTSTICK: 'left_stick',
            SDL_CONTROLLER_BUTTON_RIGHTSTICK: 'right_stick',
            SDL_CONTROLLER_BUTTON_LEFTSHOULDER: 'left_shoulder',
            SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: 'right_shoulder',
            SDL_CONTROLLER_BUTTON_DPAD_UP: 'd_pad_up',
            SDL_CONTROLLER_BUTTON_DPAD_DOWN: 'd_pad_down',
            SDL_CONTROLLER_BUTTON_DPAD_LEFT: 'd_pad_left',
            SDL_CONTROLLER_BUTTON_DPAD_RIGHT: 'd_pad_right',
            SDL_CONTROLLER_BUTTON_MISC1: 'misc1',
            SDL_CONTROLLER_BUTTON_PADDLE1: 'paddle1',
            SDL_CONTROLLER_BUTTON_PADDLE2: 'paddle2',
            SDL_CONTROLLER_BUTTON_PADDLE3: 'paddle2',
            SDL_CONTROLLER_BUTTON_PADDLE4: 'paddle3',
            SDL_CONTROLLER_BUTTON_TOUCHPAD: 'touchpad',
            SDL_CONTROLLER_BUTTON_MAX: 'max'
        }.get(event.button)
        self.state = 'pressed' if event.state == SDL_PRESSED else 'released'


class ControllerDeviceEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        if self.type == SDL_JOYDEVICEADDED:
            self.index = event.which
            self.instance_id = 0
        else:
            self.index = 0
            self.instance_id = event.which


class ControllerTouchpadEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.touchpad = event.touchpad
        self.finger = event.finger
        self.pos = (event.x, event.y)
        self.pressure = event.pressure


class ControllerSensorEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        self.instance_id = event.which
        self.sensor = event.sensor
        self.pos = (event.x, event.y)
        self.data = (event.data[0], event.data[1], event.data[2])
        self.time = event.timestamp_us / 1000000


class AudioDeviceEvent(CommonEvent):
    def __init__(self, event: SDL_Event) -> None:
        super().__init__(event)
        if self.type == SDL_AUDIODEVICEADDED:
            self.which = event.which
            self.event = 'add'
        else:
            self.which = event.which
            self.event = 'remove'
        if event.iscapture == 0:
            self.device_type = 'playback'
        else:
            self.device_type = 'recording'


class DropEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        if self.type == SDL_DROPFILE or self.type == SDL_DROPTEXT:
            self.file = app.bts(event.file)
            self.drop_type = 'file' if self.type == SDL_DROPFILE else 'text'
            self.drop_state = None
        else:
            self.file = None
            self.drop_type = None
            self.drop_state = 'begin' if self.type == SDL_DROPBEGIN else 'complete'
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class TouchFingerEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        if self.type == SDL_FINGERMOTION:
            self.event = 'move'
        else:
            self.event = 'down' if self.type == SDL_FINGERDOWN else 'up'
        self.touch_id = event.touchId
        self.finger_id = event.fingerId
        self.pos = (event.x, event.y)
        self.d_pos = (event.dx, event.dy)
        self.pressure = event.pressure
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class KeyboardEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.event = 'down' if self.type == SDL_KEYDOWN else 'up'
        self.state = 'pressed' if event.state == SDL_PRESSED else 'released'
        self.repeat = event.repeat
        if self.repeat:
            self.event = 'hold'
        self.scancode_id = event.keysym.scancode
        self.scancode = app.bts(SDL_GetScancodeName(self.scancode_id))
        self.sym_id = event.keysym.sym
        self.sym = app.bts(SDL_GetKeyName(self.sym_id))
        self.mod = event.keysym.mod
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class MouseMotionEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.which = event.which
        self.emulated = self.which == SDL_TOUCH_MOUSEID
        self.state_num = event.state
        self.state = (
            bool(event.state & SDL_BUTTON_LMASK),
            bool(event.state & SDL_BUTTON_MMASK),
            bool(event.state & SDL_BUTTON_RMASK),
            bool(event.state & SDL_BUTTON_X1MASK),
            bool(event.state & SDL_BUTTON_X2MASK)
        )
        self.pos = (event.x, event.y)
        self.rel = (event.xrel, event.yrel)
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class MouseButtonEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.button_event = 'down' if event.type == SDL_MOUSEBUTTONDOWN else 'up'
        self.which = event.which
        self.emulated = self.which == SDL_TOUCH_MOUSEID
        self.button_id = event.button
        self.button = {
            SDL_BUTTON_LEFT: 0,
            SDL_BUTTON_MIDDLE: 1,
            SDL_BUTTON_RIGHT: 2,
            SDL_BUTTON_X1: 3,
            SDL_BUTTON_X2: 4
        }.get(self.button_id)
        self.state = 'pressed' if event.state == SDL_PRESSED else 'released'
        self.clicks = event.clicks
        self.pos = (event.x, event.y)
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class MouseWheelEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.which = event.which
        self.emulated = self.which == SDL_TOUCH_MOUSEID
        self.pos = (event.x, event.y)
        self.direction = 'flipped' if event.direction == SDL_MOUSEWHEEL_FLIPPED else 'normal'
        self.precise_x = event.preciseX
        self.precise_y = event.preciseY
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class TextEditingEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.text = app.bts(event.text, 'utf-8')
        self.start = event.start
        self.length = event.length
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class TextInputEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.text = app.bts(event.text, 'utf-8')
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]


class DisplayEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.display = Display(event.display, app)
        if event.event == SDL_DISPLAYEVENT_ORIENTATION:
            self.event = 'orientation_change'
        elif event.event == SDL_DISPLAYEVENT_CONNECTED:
            self.event = 'connect'
        elif event.event == SDL_DISPLAYEVENT_DISCONNECTED:
            self.event = 'disconnect'
        else:
            self.event = None
        self.data = event.data1


class WindowEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.data1 = event.data1
        self.data2 = event.data2
        self.event = event.event
        self.padding1 = event.padding1
        self.padding2 = event.padding2
        self.padding3 = event.padding3
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id[0]
        self.window = app.windows[self.window_id]
