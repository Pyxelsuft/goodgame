import ctypes
from .events import DropEvent, TouchFingerEvent, KeyboardEvent, MouseMotionEvent, MouseButtonEvent, MouseWheelEvent,\
    TextEditingEvent, TextInputEvent, WindowEvent, default_window_id
from .video import DisplayMode, PixelFormat
from .surface import Surface
from .opengl import GLContext
from sdl2 import *

try:
    SDL_WINDOWEVENT_ICCPROF_CHANGED = SDL_WINDOWEVENT_ICCPROF_CHANGED
except NameError:
    SDL_WINDOWEVENT_ICCPROF_CHANGED = 17
try:
    SDL_WINDOWEVENT_DISPLAY_CHANGED = SDL_WINDOWEVENT_DISPLAY_CHANGED
except NameError:
    SDL_WINDOWEVENT_DISPLAY_CHANGED = 18


class Window:
    def __init__(
            self,
            app: any,
            pos: any = None,
            size: any = (640, 480),
            skip_taskbar: bool = False,
            window_type: str = None,
            context: str = None
    ) -> None:
        self.destroyed = True
        self.app = app
        self.pos = pos or (SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED)
        self.size = size
        self.window = SDL_CreateWindow(
            app.stb('Good Window'),
            int(self.pos[0]), int(self.pos[1]),
            int(self.size[0]), int(self.size[1]),
            SDL_WINDOW_ALLOW_HIGHDPI | SDL_WINDOW_HIDDEN | (SDL_WINDOW_UTILITY if window_type == 'utility' else (
                SDL_WINDOW_TOOLTIP if window_type == 'tooltip' else (
                    SDL_WINDOW_POPUP_MENU if window_type == 'popup_menu' else 0
                )
            )) | (SDL_WINDOW_SKIP_TASKBAR if skip_taskbar else 0) | (SDL_WINDOW_OPENGL if context == 'opengl' else 0) |
            (SDL_WINDOW_VULKAN if context == 'vulkan' else 0)
        )
        if not self.window:
            app.raise_error()
        self.mouse_rect = None
        self.shown = False
        self.borderless = False
        self.maximized = False
        self.minimized = False
        self.resizable = False
        self.always_on_top = False
        self.input_focused = False
        self.mouse_focused = False
        self.emulate_mouse_with_touch = False
        self.opacity = 1.0
        self.brightness = 1.0
        self.display_id = SDL_GetWindowDisplayIndex(self.window)
        self.min_size = (0, 0)
        self.max_size = (0, 0)
        self.event_map = {
            SDL_WINDOWEVENT_SHOWN: self.on_show,
            SDL_WINDOWEVENT_HIDDEN: self.on_hide,
            SDL_WINDOWEVENT_EXPOSED: self.on_expose,
            SDL_WINDOWEVENT_MOVED: self.on_move,
            SDL_WINDOWEVENT_RESIZED: self.on_resize,
            SDL_WINDOWEVENT_SIZE_CHANGED: self.on_size_change,
            SDL_WINDOWEVENT_MINIMIZED: self.on_minimize,
            SDL_WINDOWEVENT_MAXIMIZED: self.on_maximize,
            SDL_WINDOWEVENT_RESTORED: self.on_restore,
            SDL_WINDOWEVENT_ENTER: self.on_enter,
            SDL_WINDOWEVENT_LEAVE: self.on_leave,
            SDL_WINDOWEVENT_FOCUS_GAINED: self.on_focus_gain,
            SDL_WINDOWEVENT_FOCUS_LOST: self.on_focus_lose,
            SDL_WINDOWEVENT_CLOSE: self.on_close,
            SDL_WINDOWEVENT_TAKE_FOCUS: self.on_take_focus,
            SDL_WINDOWEVENT_ICCPROF_CHANGED: self.on_icc_profile_change,
            SDL_WINDOWEVENT_DISPLAY_CHANGED: self.on_display_change
        }
        borders = [ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(0)]
        SDL_GetWindowBordersSize(self.window, *borders)
        self.borders_size = (borders[0].value, borders[1].value, borders[2].value, borders[3].value)
        self.pixel_format = PixelFormat(SDL_GetWindowPixelFormat(self.window), app)
        self.update_pos()
        self.update_size()
        self.display_mode = self.get_display_mode()
        self.id = SDL_GetWindowID(self.window)
        default_window_id[0] = self.id
        app.windows[self.id] = self
        self.destroyed = False
        # TODO:
        #  support creating contexts
        #  gamma ramp, hit test (maybe no?) and other spec. things

    def create_gl_context(self) -> GLContext:
        return GLContext(self, SDL_GL_CreateContext(self.window))

    @staticmethod
    def get_mouse_buttons() -> tuple:
        state = SDL_GetMouseState(None, None)
        return (
            bool(state & SDL_BUTTON_LMASK),
            bool(state & SDL_BUTTON_MMASK),
            bool(state & SDL_BUTTON_RMASK),
            bool(state & SDL_BUTTON_X1MASK),
            bool(state & SDL_BUTTON_X2MASK)
        )

    @staticmethod
    def get_mouse_pos() -> tuple:
        x_ptr, y_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_GetMouseState(x_ptr, y_ptr)
        return x_ptr.value, y_ptr.value

    def set_mouse_pos(self, pos: any) -> None:
        SDL_WarpMouseInWindow(self.window, int(pos[0]), int(pos[1]))

    @staticmethod
    def screen_saver(enabled: bool) -> None:
        (SDL_EnableScreenSaver if enabled else SDL_DisableScreenSaver)()

    @staticmethod
    def is_screen_saver_enabled() -> bool:
        return bool(SDL_IsScreenSaverEnabled())

    def flash(self) -> None:
        SDL_FlashWindow(self.window)

    def focus_input(self) -> None:
        SDL_SetWindowInputFocus(self.window)

    def make_modal(self, parent_window: any) -> None:
        SDL_SetWindowModalFor(self.window, parent_window.window)

    def set_mouse_rect(self, mouse_rect: any = None) -> None:
        SDL_SetWindowMouseRect(
            self.window,
            mouse_rect and SDL_Rect(int(mouse_rect[0]), int(mouse_rect[1]), int(mouse_rect[2]), int(mouse_rect[3]))
        )
        self.mouse_rect = mouse_rect

    def set_mouse_grab(self, enabled: bool) -> None:
        SDL_SetWindowMouseGrab(self.window, enabled)

    def set_keyboard_grab(self, enabled: bool) -> None:
        SDL_SetWindowKeyboardGrab(self.window, enabled)

    def get_icc_profile(self) -> bytes:
        size_ptr = ctypes.c_size_t()
        data_ptr = SDL_GetWindowICCProfile(self.window, size_ptr)
        data_buf = (ctypes.c_uint8 * size_ptr.value).from_address(data_ptr)
        return bytes(data_buf[:size_ptr.value])  # noqa

    def set_title(self, title: str) -> None:
        SDL_SetWindowTitle(self.window, self.app.stb(title))

    def set_grab(self, grabbed: bool) -> None:
        SDL_SetWindowGrab(self.window, grabbed)

    def get_grab(self) -> bool:
        return SDL_GetWindowGrab(self.window) == SDL_TRUE

    def get_display_mode(self) -> DisplayMode:
        display_mode = SDL_DisplayMode()
        SDL_GetWindowDisplayMode(self.window, display_mode)
        return DisplayMode(display_mode, self.app)

    def set_display_mode(self, display_mode: DisplayMode) -> None:
        SDL_SetWindowDisplayMode(self.window, display_mode.as_dm())
        self.display_mode = self.get_display_mode()

    def show(self) -> None:
        SDL_ShowWindow(self.window)
        self.update_flags()

    def hide(self) -> None:
        SDL_HideWindow(self.window)
        self.update_flags()

    def restore(self) -> None:
        SDL_RestoreWindow(self.window)
        self.update_flags()

    def maximize(self) -> None:
        SDL_MaximizeWindow(self.window)
        self.update_flags()

    def minimize(self) -> None:
        SDL_MinimizeWindow(self.window)
        self.update_flags()

    def get_hwnd(self) -> int:
        wm_info = SDL_SysWMinfo()
        SDL_VERSION(wm_info.version)
        SDL_GetWindowWMInfo(self.window, wm_info)
        return wm_info.info.win.window

    def update_flags(self) -> None:
        flags = SDL_GetWindowFlags(self.window)
        self.maximized = bool(flags & SDL_WINDOW_MAXIMIZED)
        self.minimized = bool(flags & SDL_WINDOW_MINIMIZED)
        self.shown = bool(flags & SDL_WINDOW_SHOWN)
        self.input_focused = bool(flags & SDL_WINDOW_INPUT_FOCUS)
        self.mouse_focused = bool(flags & SDL_WINDOW_MOUSE_FOCUS)
        self.brightness = SDL_GetWindowBrightness(self.window)

    def update_pos(self) -> None:
        x_ptr, y_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_GetWindowPosition(self.window, x_ptr, y_ptr)
        self.pos = x_ptr.value, y_ptr.value

    def update_size(self) -> None:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_GetWindowSize(self.window, w_ptr, h_ptr)
        self.size = w_ptr.value, h_ptr.value

    def set_pos(self, pos: any) -> None:
        if not pos:
            pos = (SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED)
        SDL_SetWindowPosition(self.window, int(pos[0]), int(pos[1]))
        self.update_pos()

    def set_size(self, size: any) -> None:
        SDL_SetWindowSize(self.window, int(size[0]), int(size[1]))
        self.update_size()

    def set_min_size(self, min_size: any) -> None:
        self.min_size = min_size
        SDL_SetWindowMinimumSize(self.window, int(min_size[0]), int(min_size[1]))
        self.update_size()

    def set_max_size(self, max_size: any) -> None:
        self.max_size = max_size
        SDL_SetWindowMaximumSize(self.window, int(max_size[0]), int(max_size[1]))
        self.update_size()

    def set_window_mode(self, mode: str = 'windowed') -> None:
        full_screen = 0
        if mode == 'full_screen':
            full_screen |= SDL_WINDOW_FULLSCREEN
        elif mode == 'desktop':
            full_screen |= SDL_WINDOW_FULLSCREEN_DESKTOP
        elif not mode == 'windowed':
            raise RuntimeError('Only full_screen, desktop and windowed modes are allowed!')
        SDL_SetWindowFullscreen(self.window, full_screen)

    def set_borderless(self, borderless: bool) -> None:
        self.borderless = borderless
        SDL_SetWindowBordered(self.window, not borderless)

    def set_resizable(self, resizable: bool) -> None:
        self.resizable = resizable
        SDL_SetWindowResizable(self.window, resizable)

    def set_always_on_top(self, always_on_top: bool) -> None:
        self.always_on_top = always_on_top
        SDL_SetWindowAlwaysOnTop(self.window, always_on_top)

    def set_opacity(self, opacity: float) -> None:
        self.opacity = opacity
        SDL_SetWindowOpacity(self.window, opacity)

    def set_brightness(self, brightness: float) -> None:
        SDL_SetWindowBrightness(self.window, brightness)
        self.update_size()

    def show_message_box(
            self,
            title: str,
            text: str,
            icon_type: str = None
    ) -> None:
        return self.app.show_message_box(title, text, icon_type, self)

    def is_screen_keyboard_shown(self) -> bool:
        return bool(SDL_IsScreenKeyboardShown(self.window))

    def set_icon(self, surf: Surface) -> None:
        SDL_SetWindowIcon(self.window, surf.surface)

    def raise_self(self) -> None:
        SDL_RaiseWindow(self.window)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.destroyed = True
        SDL_DestroyWindow(self.window)
        del self.app.windows[self.id]
        del self.app
        return False

    def on_drop_file(self, event: DropEvent) -> None:
        pass

    def on_drop_text(self, event: DropEvent) -> None:
        pass

    def on_drop_begin(self, event: DropEvent) -> None:
        pass

    def on_drop_complete(self, event: DropEvent) -> None:
        pass

    def on_finger_move(self, event: TouchFingerEvent) -> None:
        pass

    def on_finger_down(self, event: TouchFingerEvent) -> None:
        pass

    def on_finger_up(self, event: TouchFingerEvent) -> None:
        pass

    def on_key_down(self, event: KeyboardEvent) -> None:
        pass

    def on_key_up(self, event: KeyboardEvent) -> None:
        pass

    def on_text_edit(self, event: TextEditingEvent) -> None:
        pass

    def on_text_edit_ext(self, event: TextEditingEvent) -> None:
        pass

    def on_mouse_move(self, event: MouseMotionEvent) -> None:
        pass

    def on_mouse_down(self, event: MouseButtonEvent) -> None:
        pass

    def on_mouse_up(self, event: MouseButtonEvent) -> None:
        pass

    def on_mouse_wheel(self, event: MouseWheelEvent) -> None:
        pass

    def on_text_input(self, event: TextInputEvent) -> None:
        pass

    def on_show(self, event: WindowEvent) -> None:
        pass

    def on_hide(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_expose(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_move(self, event: WindowEvent) -> None:
        self.pos = event.data1, event.data2

    def on_resize(self, event: WindowEvent) -> None:
        self.size = event.data1, event.data2

    def on_size_change(self, event: WindowEvent) -> None:
        self.size = event.data1, event.data2

    def on_minimize(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_maximize(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_restore(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_enter(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_leave(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_focus_gain(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_focus_lose(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_close(self, event: WindowEvent) -> None:
        pass

    def on_take_focus(self, event: WindowEvent) -> None:
        self.update_flags()

    def on_icc_profile_change(self, event: WindowEvent) -> None:
        pass

    def on_display_change(self, event: WindowEvent) -> None:
        self.display_mode = self.get_display_mode()

    def __del__(self) -> None:
        self.destroy()
