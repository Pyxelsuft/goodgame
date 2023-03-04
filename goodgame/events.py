from sdl2 import *
from .video import Display

try:
    SDL_TOUCH_MOUSEID = SDL_TOUCH_MOUSEID
except NameError:
    SDL_TOUCH_MOUSEID = 2 ** 32 - 1

default_window_id = 0


class CommonEvent:
    def __init__(self, event: SDL_Event) -> None:
        self.event = event
        self.timestamp = event.timestamp
        self.type = event.type


class QuitEvent(CommonEvent):
    pass


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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
        self.window = app.windows[self.window_id]


class TextEditingEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.text = app.bts(event.text, 'utf-8')
        self.start = event.start
        self.length = event.length
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
        self.window = app.windows[self.window_id]


class TextInputEvent(CommonEvent):
    def __init__(self, event: SDL_Event, app: any) -> None:
        super().__init__(event)
        self.text = app.bts(event.text, 'utf-8')
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
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
        self.window_id = event.windowID if hasattr(event, 'windowID') else default_window_id
        self.window = app.windows[self.window_id]
