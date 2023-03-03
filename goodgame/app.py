import os
import ctypes
from .exceptions import FlagNotFoundError, SDLError
from .events import CommonEvent, QuitEvent, AudioDeviceEvent, DropEvent, TouchFingerEvent, KeyboardEvent,\
    MouseMotionEvent, MouseButtonEvent, MouseWheelEvent, TextEditingEvent, TextInputEvent, DisplayEvent, WindowEvent
from .sdl import SDLVersion, sdl_dir
from .surface import Surface
from .video import PixelFormat
from .window import Window
from sdl2 import *

try:
    from sdl2.sdlimage import *
except Exception as _err:
    print(f'Failed to import SDL2_image [{_err}]. Image loading will be disabled!')
try:
    from sdl2.sdlmixer import *
except Exception as _err:
    print(f'Failed to import SDL2_mixer [{_err}]. Mixer will be disabled!')
try:
    from sdl2.sdlttf import *
except Exception as _err:
    print(f'Failed to import SDL2_ttf [{_err}]. Font loading and rendering will be disabled!')


class App:
    def __init__(self) -> None:
        self.destroyed = True
        self.encoding = 'utf-8'
        if SDL_BYTEORDER == SDL_LIL_ENDIAN:
            self.endian = 'little'
            self.default_rgb_mask = (0x0000FF, 0x00FF00, 0xFF0000, 0)
            self.default_rgba_mask = (0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
        else:
            self.endian = 'big'
            self.default_rgb_mask = (0xFF0000, 0x00FF00, 0x0000FF, 0)
            self.default_rgba_mask = (0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF)
        self.cwd = os.getcwd()
        self.init_flags = {
            'sdl': 0,
            'image': 0,
            'mixer': 0,
            'has_sdl': False,
            'has_image': False,
            'has_mixer': False,
            'has_ttf': False
        }
        self.blend_map = {
            'none': SDL_BLENDMODE_NONE,
            'blend': SDL_BLENDMODE_BLEND,
            'add': SDL_BLENDMODE_ADD,
            'mod': SDL_BLENDMODE_MOD,
            'mul': SDL_BLENDMODE_MUL
        }
        self.r_blend_map = {b: a for a, b in self.blend_map.items()}
        self.event_map = {
            SDL_AUDIODEVICEADDED: lambda: self.on_audio_device_add(AudioDeviceEvent(self.sdl_event.adevice)),
            SDL_AUDIODEVICEREMOVED: lambda: self.on_audio_device_remove(AudioDeviceEvent(self.sdl_event.adevice)),
            SDL_QUIT: lambda: self.on_quit(QuitEvent(self.sdl_event.quit)),
            SDL_DROPFILE: lambda: self.on_drop_file(DropEvent(self.sdl_event.drop, self)),
            SDL_DROPTEXT: lambda: self.on_drop_text(DropEvent(self.sdl_event.drop, self)),
            SDL_DROPBEGIN: lambda: self.on_drop_begin(DropEvent(self.sdl_event.drop, self)),
            SDL_DROPCOMPLETE: lambda: self.on_drop_complete(DropEvent(self.sdl_event.drop, self)),
            SDL_FINGERMOTION: lambda: self.on_finger_motion(TouchFingerEvent(self.sdl_event.tfinger, self)),
            SDL_FINGERDOWN: lambda: self.on_finger_down(TouchFingerEvent(self.sdl_event.tfinger, self)),
            SDL_FINGERUP: lambda: self.on_finger_up(TouchFingerEvent(self.sdl_event.tfinger, self)),
            SDL_KEYDOWN: lambda: self.on_key_down(KeyboardEvent(self.sdl_event.key, self)),
            SDL_KEYUP: lambda: self.on_key_up(KeyboardEvent(self.sdl_event.key, self)),
            SDL_TEXTEDITING: lambda: self.on_text_edit(TextEditingEvent(self.sdl_event.edit, self)),
            SDL_TEXTEDITING_EXT: lambda: self.on_text_edit_ext(TextEditingEvent(self.sdl_event.edit, self)),
            SDL_MOUSEMOTION: lambda: self.on_mouse_move(MouseMotionEvent(self.sdl_event.motion, self)),
            SDL_MOUSEBUTTONDOWN: lambda: self.on_mouse_down(MouseButtonEvent(self.sdl_event.button, self)),
            SDL_MOUSEBUTTONUP: lambda: self.on_mouse_up(MouseButtonEvent(self.sdl_event.button, self)),
            SDL_MOUSEWHEEL: lambda: self.on_mouse_wheel(MouseWheelEvent(self.sdl_event.wheel, self)),
            SDL_TEXTINPUT: lambda: self.on_text_input(TextInputEvent(self.sdl_event.text, self)),
            SDL_DISPLAYEVENT: lambda: self.on_display_event(DisplayEvent(self.sdl_event.display, self)),
            SDL_WINDOWEVENT: lambda: self.on_window_event(WindowEvent(self.sdl_event.window, self)),
            SDL_APP_TERMINATING: lambda: self.on_terminate(CommonEvent(self.sdl_event.common)),
            SDL_APP_LOWMEMORY: lambda: self.on_low_memory(CommonEvent(self.sdl_event.common)),
            SDL_APP_WILLENTERBACKGROUND: lambda: self.on_will_enter_background(CommonEvent(self.sdl_event.common)),
            SDL_APP_DIDENTERBACKGROUND: lambda: self.on_did_enter_background(CommonEvent(self.sdl_event.common)),
            SDL_APP_WILLENTERFOREGROUND: lambda: self.on_will_enter_foreground(CommonEvent(self.sdl_event.common)),
            SDL_APP_DIDENTERFOREGROUND: lambda: self.on_did_enter_foreground(CommonEvent(self.sdl_event.common)),
            SDL_LOCALECHANGED: lambda: self.on_locale_change(CommonEvent(self.sdl_event.common)),
            SDL_KEYMAPCHANGED: lambda: self.on_keymap_change(CommonEvent(self.sdl_event.common)),
            SDL_RENDER_TARGETS_RESET: lambda: self.on_render_targets_reset(CommonEvent(self.sdl_event.common)),
            SDL_RENDER_DEVICE_RESET: lambda: self.on_render_device_reset(CommonEvent(self.sdl_event.common))
        }
        self.windows = {}
        self.running = False
        self.rel_mouse_mode = False
        self.mouse_capture = False
        self.keyboard_state_ptr = SDL_GetKeyboardState(None)
        self.sdl_event = SDL_Event()
        self.destroyed = False
        # TODO:
        #  async sprites loader
        #  math
        #  RW ops
        #  gifs (animations) loading
        #  joysticks, haptics, sensors, gestures, touch
        #  pixels (palettes, etc)
        #  In window functions move to Window?
        #  Custom message box

    def get_key_state(self, key: str) -> bool:
        return bool(self.keyboard_state_ptr[SDL_GetScancodeFromName(self.stb(key))])

    @staticmethod
    def get_img_version() -> tuple:
        ver = IMG_Linked_Version().contents
        return ver.major, ver.minor, ver.patch

    def set_mouse_capture(self, enabled: bool) -> None:
        self.mouse_capture = enabled
        SDL_CaptureMouse(enabled)

    def set_rel_mouse(self, enabled: bool) -> None:
        self.rel_mouse_mode = enabled
        SDL_SetRelativeMouseMode(enabled)

    @staticmethod
    def set_mouse_pos(pos: any) -> None:
        SDL_WarpMouseGlobal(int(pos[0]), int(pos[1]))

    @staticmethod
    def get_mouse_buttons() -> tuple:
        state = SDL_GetGlobalMouseState(None, None)
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
        SDL_GetGlobalMouseState(x_ptr, y_ptr)
        return x_ptr.value, y_ptr.value

    @staticmethod
    def get_rel_mouse_buttons() -> tuple:
        state = SDL_GetRelativeMouseState(None, None)
        return (
            bool(state & SDL_BUTTON_LMASK),
            bool(state & SDL_BUTTON_MMASK),
            bool(state & SDL_BUTTON_RMASK),
            bool(state & SDL_BUTTON_X1MASK),
            bool(state & SDL_BUTTON_X2MASK)
        )

    @staticmethod
    def get_rel_mouse_pos() -> tuple:
        x_ptr, y_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_GetRelativeMouseState(x_ptr, y_ptr)
        return x_ptr.value, y_ptr.value

    @staticmethod
    def get_power_info() -> dict:
        seconds_ptr, percent_ptr = ctypes.c_int(), ctypes.c_int()
        power_state = SDL_GetPowerInfo(seconds_ptr, percent_ptr)
        return {
            'power_state': {
                SDL_POWERSTATE_UNKNOWN: 'unknown',
                SDL_POWERSTATE_ON_BATTERY: 'on_battery',
                SDL_POWERSTATE_NO_BATTERY: 'no_battery',
                SDL_POWERSTATE_CHARGING: 'charging',
                SDL_POWERSTATE_CHARGED: 'charged'
            }.get(power_state),
            'seconds_left': None if seconds_ptr.value == -1 else seconds_ptr.value,
            'percentage': None if percent_ptr.value == -1 else percent_ptr.value
        }

    def get_pref_path(self, app: str, org: str = None) -> str:
        pref_path = SDL_GetPrefPath(org and self.stb(org), app and self.stb(app))
        if not pref_path:
            self.raise_error()
        return self.bts(pref_path)

    def get_base_path(self) -> str:
        base_path = SDL_GetBasePath()
        if not base_path:
            self.raise_error()
        return self.bts(base_path)

    @staticmethod
    def get_keyboard_state() -> tuple:
        return bool(SDL_IsTextInputActive()), bool(SDL_IsTextInputShown()), bool(SDL_HasScreenKeyboardSupport())

    @staticmethod
    def clear_text_input() -> None:
        SDL_ClearComposition()

    @staticmethod
    def enable_text_input(enabled: bool) -> None:
        (SDL_StartTextInput if enabled else SDL_StopTextInput)()

    @staticmethod
    def get_time() -> float:
        return SDL_GetTicks64() / 1000

    def sleep(self, time: float) -> None:
        wait_for = self.get_time() + time
        while self.get_time() < wait_for:
            continue

    def set_clipboard_text(self, text: str) -> None:
        SDL_SetClipboardText(self.stb(text))

    def set_primary_selection_text(self, text: str) -> None:
        SDL_SetPrimarySelectionText(self.stb(text))

    def get_clipboard_text(self) -> str:
        if not SDL_HasClipboardText():
            return ''
        return self.bts(SDL_GetClipboardText())

    def get_primary_selection_text(self) -> str:
        if not SDL_HasPrimarySelectionText():
            return ''
        return self.bts(SDL_GetPrimarySelectionText())

    def get_platform(self) -> str:
        return self.bts(SDL_GetPlatform())

    def open_url(self, url: str) -> None:
        if SDL_OpenURL(self.stb(url)) < 0:
            self.raise_error()

    def show_message_box(
            self,
            title: str,
            text: str,
            icon_type: str = None,
            window: Window = None
    ) -> None:
        flags = 0
        if icon_type == 'information':
            flags |= SDL_MESSAGEBOX_INFORMATION
        elif icon_type == 'warning':
            flags |= SDL_MESSAGEBOX_WARNING
        elif icon_type == 'error':
            flags |= SDL_MESSAGEBOX_ERROR
        if SDL_ShowSimpleMessageBox(flags, self.stb(title), self.stb(text), window and window.window) < 0:
            self.raise_error()

    def get_preferred_locales(self) -> tuple:
        return tuple(
            {'lang': self.bts(_x.language), 'country': self.bts(_x.country)} for _x in SDL_GetPreferredLocales()
        )

    def get_sdl_info(self) -> dict:
        ver_ptr = SDL_version()
        SDL_GetVersion(ver_ptr)
        return {
            'version': (ver_ptr.major, ver_ptr.minor, ver_ptr.patch),
            'revision': self.bts(SDL_GetRevision())
        }

    @staticmethod
    def get_cpu_info() -> dict:
        return {
            'count': SDL_GetCPUCount(),
            'cache_line_size': SDL_GetCPUCacheLineSize(),
            'ram': SDL_GetSystemRAM(),
            'simd_alignment': SDL_SIMDGetAlignment(),
            'RDTSC': bool(SDL_HasRDTSC()),
            'AltiVec': bool(SDL_HasAltiVec()),
            'MMX': bool(SDL_HasMMX()),
            '3DNow': bool(SDL_Has3DNow()),
            'SSE': bool(SDL_HasSSE()),
            'SSE2': bool(SDL_HasSSE2()),
            'SSE3': bool(SDL_HasSSE3()),
            'SSE41': bool(SDL_HasSSE41()),
            'SSE42': bool(SDL_HasSSE42()),
            'AVX': bool(SDL_HasAVX()),
            'AVX2': bool(SDL_HasAVX2()),
            'AVX512F': bool(SDL_HasAVX512F()),
            'ARMSIMD': bool(SDL_HasARMSIMD()),
            'NEON': bool(SDL_HasNEON()),
            'LSX': bool(SDL_HasLSX()),
            'LASX': bool(SDL_HasLASX())
        }

    @staticmethod
    def alloc_pixel_format(pixel_format: PixelFormat) -> SDL_PixelFormat:
        return SDL_AllocFormat(pixel_format.pixel_format)

    def surface_from_bytes(
            self, data: any, size: any, depth: int, pitch: int,
            mask: any = (0, 0, 0, 0), pixel_format: PixelFormat = None
    ) -> Surface:
        if pixel_format:
            surf = SDL_CreateRGBSurfaceWithFormatFrom(
                data, int(size[0]), int(size[1]), depth, pitch, mask[0],
                mask[1], mask[2], mask[3], pixel_format.pixel_format
            )
        else:
            surf = SDL_CreateRGBSurfaceFrom(
                data, int(size[0]), int(size[1]), depth, pitch, mask[0], mask[1], mask[2], mask[3]
            )
        if not surf:
            self.raise_error()
        return Surface(surf, self)

    def create_rgb_surface(
            self, size: any, depth: int = 32, mask: any = (0, 0, 0, 0), pixel_format: PixelFormat = None
    ) -> Surface:
        if pixel_format:
            surf = SDL_CreateRGBSurfaceWithFormat(
                0, int(size[0]), int(size[1]), depth, mask[0], mask[1], mask[2], mask[3], pixel_format.pixel_format
            )
        else:
            surf = SDL_CreateRGBSurface(0, int(size[0]), int(size[1]), depth, mask[0], mask[1], mask[2], mask[3])
        if not surf:
            self.raise_error()
        return Surface(surf, self)

    def surface_from_bmp(self, path: str) -> Surface:
        surf = SDL_LoadBMP(self.stb(path))
        if not surf:
            self.raise_error()
        return Surface(surf, self)

    def surface_from_file(self, path: str) -> Surface:
        surf = IMG_Load(self.stb(path))
        if not surf:
            self.raise_error(IMG_GetError)
        return Surface(surf, self)

    def poll_events(self) -> None:
        while SDL_PollEvent(self.sdl_event):
            (self.event_map.get(self.sdl_event.type) or self.on_unknown_event)()

    def on_unknown_event(self) -> None:
        event_names = []
        for var_name in sdl_dir:
            if not var_name.startswith('SDL_'):
                continue
            if eval(var_name) == self.sdl_event.type:
                event_names.append(var_name)
        print(f'Unknown event {self.sdl_event.type}: {", ".join(event_names)}')

    def run_loop(self) -> None:
        self.running = True
        while self.running:
            self.on_tick()

    def stop_loop(self) -> None:
        self.running = False

    def init(
            self,
            sdl_flags_list: any = ('video', 'events', 'timer'),
            image_formats: any = ('png', 'jpg'),
            mixer_formats: any = None,
            init_ttf: bool = True
    ) -> None:
        if sdl_flags_list:
            flag_map = {
                'timer': SDL_INIT_TIMER,
                'audio': SDL_INIT_AUDIO,
                'video': SDL_INIT_VIDEO,
                'joystick': SDL_INIT_JOYSTICK,
                'haptic': SDL_INIT_HAPTIC,
                'game_controller': SDL_INIT_GAMECONTROLLER,
                'events': SDL_INIT_EVENTS,
                'sensor': SDL_INIT_SENSOR
            }
            flags = 0
            for flag_str in sdl_flags_list:
                flag = flag_map.get(flag_str)
                if not flag:
                    raise FlagNotFoundError(f'Flag {flag_str} not found among: {", ".join(flag_map.keys())}')
                flags |= flag
            flags |= self.init_flags['sdl']
            diff = self.init_flags['sdl'] ^ flags
            if diff and SDL_Init(diff) < 0:
                self.raise_error()
            self.init_flags['sdl'] = flags
            self.init_flags['has_sdl'] = True
        if image_formats:
            flag_map = {
                'png': IMG_INIT_PNG,
                'jpg': IMG_INIT_JPG,
                'jxl': IMG_INIT_JXL,
                'tif': IMG_INIT_TIF,
                'avif': IMG_INIT_AVIF,
                'webp': IMG_INIT_WEBP
            }
            flags = 0
            for flag_str in image_formats:
                flag = flag_map.get(flag_str)
                if not flag:
                    raise FlagNotFoundError(f'Format {flag_str} not found among: {", ".join(flag_map.keys())}')
                flags |= flag
            flags |= self.init_flags['image']
            diff = self.init_flags['image'] ^ flags
            if not IMG_Init(diff) == diff:
                self.raise_error(IMG_GetError)
            self.init_flags['image'] = flags
            self.init_flags['has_image'] = True
        if mixer_formats:
            flag_map = {
                'mp3': MIX_INIT_MP3,
                'mid': MIX_INIT_MID,
                'mod': MIX_INIT_MOD,
                'ogg': MIX_INIT_OGG,
                'flac': MIX_INIT_FLAC,
                'opus': MIX_INIT_OPUS
            }
            flags = 0
            for flag_str in mixer_formats:
                flag = flag_map.get(flag_str)
                if not flag:
                    raise FlagNotFoundError(f'Format {flag_str} not found among: {", ".join(flag_map.keys())}')
                flags |= flag
            flags |= self.init_flags['mixer']
            diff = self.init_flags['mixer'] ^ flags
            if not Mix_Init(diff) == diff:
                self.raise_error(Mix_GetError)
            self.init_flags['mixer'] = flags
            self.init_flags['has_mixer'] = True
        if init_ttf and not self.init_flags['has_ttf']:
            if TTF_Init() < 0:
                self.raise_error(TTF_GetError)
            self.init_flags['has_ttf'] = True

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.destroyed = False
        if self.init_flags['has_ttf']:
            self.init_flags['has_ttf'] = False
            TTF_Quit()
        if self.init_flags['has_mixer']:
            self.init_flags['has_mixer'] = False
            self.init_flags['mixer'] = 0
            Mix_Quit()
        if self.init_flags['has_image']:
            self.init_flags['has_image'] = False
            self.init_flags['image'] = 0
            IMG_Quit()
        if self.init_flags['has_sdl']:
            self.init_flags['has_sdl'] = False
            self.init_flags['sdl'] = 0
            SDL_Quit()
        return False

    def get_error(self, error_func: any = SDL_GetError) -> str:
        return self.bts(error_func())

    def raise_error(self, error_func: any = SDL_GetError) -> None:
        raise SDLError(self.get_error(error_func))

    def stb(self, str_to_convert: str, encoding: str = None) -> bytes:
        return str_to_convert.encode(encoding or self.encoding, errors='replace')

    def bts(self, bytes_to_convert: bytes, encoding: str = None) -> str:
        return bytes_to_convert.decode(encoding or self.encoding, errors='replace')

    def p(self, *path: str) -> str:
        return os.path.join(self.cwd, *path)

    @staticmethod
    def get_sdl_version() -> SDLVersion:
        ver = SDL_version()
        SDL_GetVersion(ver)
        return SDLVersion(ver)

    @staticmethod
    def print_sub_content(obj_for_displaying: any) -> None:
        for elem_name in dir(obj_for_displaying):
            if elem_name.startswith('_'):
                continue
            elem = getattr(obj_for_displaying, elem_name)
            if not hasattr(elem, '__str__'):
                continue
            print(f'{elem_name}: {elem}')

    def on_tick(self) -> None:
        pass

    def on_audio_device_add(self, event: AudioDeviceEvent) -> None:
        pass

    def on_audio_device_remove(self, event: AudioDeviceEvent) -> None:
        pass

    def on_quit(self, event: QuitEvent) -> None:
        pass

    def on_drop_file(self, event: DropEvent) -> None:  # noqa
        event.window.on_drop_file(event)

    def on_drop_text(self, event: DropEvent) -> None:  # noqa
        event.window.on_drop_text(event)

    def on_drop_begin(self, event: DropEvent) -> None:  # noqa
        event.window.on_drop_begin(event)

    def on_drop_complete(self, event: DropEvent) -> None:  # noqa
        event.window.on_drop_complete(event)

    def on_finger_motion(self, event: TouchFingerEvent) -> None:  # noqa
        event.window.on_finger_motion(event)

    def on_finger_down(self, event: TouchFingerEvent) -> None:  # noqa
        event.window.on_finger_down(event)

    def on_finger_up(self, event: TouchFingerEvent) -> None:  # noqa
        event.window.on_finger_up(event)

    def on_key_down(self, event: KeyboardEvent) -> None:  # noqa
        event.window.on_key_down(event)

    def on_key_up(self, event: KeyboardEvent) -> None:  # noqa
        event.window.on_key_up(event)

    def on_text_edit(self, event: TextEditingEvent) -> None:  # noqa
        event.window.on_text_edit(event)

    def on_text_edit_ext(self, event: TextEditingEvent) -> None:  # noqa
        event.window.on_text_edit_ext(event)

    def on_mouse_move(self, event: MouseMotionEvent) -> None:  # noqa
        if event.emulated and not event.window.emulate_mouse_with_touch:
            return
        event.window.on_mouse_move(event)

    def on_mouse_down(self, event: MouseButtonEvent) -> None:  # noqa
        if event.emulated and not event.window.emulate_mouse_with_touch:
            return
        event.window.on_mouse_down(event)

    def on_mouse_up(self, event: MouseButtonEvent) -> None:  # noqa
        if event.emulated and not event.window.emulate_mouse_with_touch:
            return
        event.window.on_mouse_up(event)

    def on_mouse_wheel(self, event: MouseWheelEvent) -> None:  # noqa
        if event.emulated and not event.window.emulate_mouse_with_touch:
            return
        event.window.on_mouse_wheel(event)

    def on_text_input(self, event: TextInputEvent) -> None:  # noqa
        event.window.on_text_input(event)

    def on_display_event(self, event: DisplayEvent) -> None:
        pass

    def on_window_event(self, event: WindowEvent) -> None:
        event.window.event_map.get(self.sdl_event.window.event)(event)

    def on_terminate(self, event: CommonEvent) -> None:
        pass

    def on_low_memory(self, event: CommonEvent) -> None:
        pass

    def on_will_enter_background(self, event: CommonEvent) -> None:
        pass

    def on_did_enter_background(self, event: CommonEvent) -> None:
        pass

    def on_will_enter_foreground(self, event: CommonEvent) -> None:
        pass

    def on_did_enter_foreground(self, event: CommonEvent) -> None:
        pass

    def on_locale_change(self, event: CommonEvent) -> None:
        pass

    def on_keymap_change(self, event: CommonEvent) -> None:
        pass

    def on_render_targets_reset(self, event: CommonEvent) -> None:
        pass

    def on_render_device_reset(self, event: CommonEvent) -> None:
        pass
    def __del__(self) -> None:
        self.destroy()
