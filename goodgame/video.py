import ctypes
import sys
from sdl2 import *


class PixelFormat:
    def __init__(self, pixel_format: int, app: any) -> None:
        self.pixel_format = pixel_format
        self.pixel_format_name = app.bts(SDL_GetPixelFormatName(self.pixel_format))
        self.pixel_type = SDL_PIXELTYPE(pixel_format)
        self.pixel_layout = SDL_PIXELLAYOUT(pixel_format)
        self.bits_per_pixel = SDL_BITSPERPIXEL(pixel_format)
        self.bytes_per_pixel = SDL_BYTESPERPIXEL(pixel_format)
        self.is_pixel_format_indexed = bool(SDL_ISPIXELFORMAT_INDEXED(pixel_format))
        self.is_pixel_format_alpha = bool(SDL_ISPIXELFORMAT_ALPHA(pixel_format))
        self.is_pixel_format_fourcc = bool(SDL_ISPIXELFORMAT_FOURCC(pixel_format))


class DisplayMode:
    def __init__(self, mode: SDL_DisplayMode = SDL_DisplayMode(), app: any = None) -> None:
        self.format = PixelFormat(mode.format, app)
        self.w = mode.w
        self.h = mode.h
        self.refresh_rate = mode.refresh_rate

    def as_dm(self) -> SDL_DisplayMode:
        return SDL_DisplayMode(self.format.pixel_format, self.w, self.h, self.refresh_rate)


class Display:
    def __init__(self, display_id: int, app: any) -> None:
        self.display_id = display_id
        self.name = app.bts(SDL_GetDisplayName(display_id))
        self.modes = []
        mode = SDL_DisplayMode()
        for i in range(SDL_GetNumDisplayModes(display_id)):
            SDL_GetDisplayMode(display_id, i, mode)
            self.modes.append(DisplayMode(mode, app))
        SDL_GetCurrentDisplayMode(self.display_id, mode)
        self.current_mode = DisplayMode(mode, app)
        SDL_GetDesktopDisplayMode(self.display_id, mode)
        self.desktop_mode = DisplayMode(mode, app)
        bounds = SDL_Rect()
        SDL_GetDisplayBounds(display_id, bounds)
        self.bounds = (bounds.x, bounds.y, bounds.w, bounds.h)
        dpi_ptr = [ctypes.c_float(0.0), ctypes.c_float(0.0), ctypes.c_float(0.0)]
        SDL_GetDisplayDPI(display_id, *dpi_ptr)
        self.d_dpi = dpi_ptr[0].value
        self.h_dpi = dpi_ptr[1].value
        self.v_dpi = dpi_ptr[2].value
        orientation_id = SDL_GetDisplayOrientation(display_id)
        if orientation_id == SDL_ORIENTATION_LANDSCAPE:
            self.orientation = 'landscape'
        elif orientation_id == SDL_ORIENTATION_LANDSCAPE_FLIPPED:
            self.orientation = 'landscape_flipped'
        elif orientation_id == SDL_ORIENTATION_PORTRAIT:
            self.orientation = 'portrait'
        elif orientation_id == SDL_ORIENTATION_PORTRAIT_FLIPPED:
            self.orientation = 'portrait_flipped'
        else:
            self.orientation = 'unknown'
        SDL_GetDisplayUsableBounds(display_id, bounds)
        self.usable_bounds = (bounds.x, bounds.y, bounds.w, bounds.h)

    def get_closest_mode(self, mode: DisplayMode) -> DisplayMode:
        display_mode = SDL_DisplayMode(mode.format.pixel_format, mode.w, mode.h, mode.refresh_rate)
        closest_mode = SDL_DisplayMode()
        SDL_GetClosestDisplayMode(self.display_id, display_mode, closest_mode)
        return DisplayMode(closest_mode)


class DisplaysManager:
    def __init__(self, app: any) -> None:
        self.displays = [Display(i, app) for i in range(SDL_GetNumVideoDisplays())]

    def get_display_rect(self, x: int, y: int, w: int, h: int) -> Display:
        screen_rect = SDL_Rect(x, y, w, h)
        return self.displays[SDL_GetRectDisplayIndex(screen_rect)]

    def get_display_point(self, x: int, y: int) -> Display:
        screen_point = SDL_Point(x, y)
        return self.displays[SDL_GetPointDisplayIndex(screen_point)]


class Backend:
    def __init__(self, backend_id: int, app: any) -> None:
        self.backend_id = backend_id
        renderer_info = SDL_RendererInfo()
        SDL_GetRenderDriverInfo(backend_id, renderer_info)
        self.name = app.bts(renderer_info.name)
        self.is_software = bool(renderer_info.flags & SDL_RENDERER_SOFTWARE)
        self.is_accelerated = bool(renderer_info.flags & SDL_RENDERER_ACCELERATED)
        self.can_vsync = bool(renderer_info.flags & SDL_RENDERER_PRESENTVSYNC)
        self.can_target_texture = bool(renderer_info.flags & SDL_RENDERER_TARGETTEXTURE)
        self.texture_formats = []
        for format_id in range(renderer_info.num_texture_formats):
            self.texture_formats.append(PixelFormat(renderer_info.texture_formats[format_id], app))
        self.max_texture_width = renderer_info.max_texture_width
        self.max_texture_height = renderer_info.max_texture_height


class BackendManager:
    def __init__(self, app: any) -> None:
        self.prefer_order = ['opengl', 'opengles2', 'opengles', 'software']
        if sys.platform == 'win32':
            win_ver = sys.getwindowsversion().major
            self.prefer_order.insert(0, 'direct3d')
            if win_ver >= 6:
                self.prefer_order.insert(0, 'direct3d11')
            if win_ver >= 10:
                self.prefer_order.insert(0, 'direct3d12')
        self.backends = [Backend(x, app) for x in range(SDL_GetNumRenderDrivers())]

    def get_by_name(self, backend_name: str) -> Backend:
        return self.backends[max(self.get_by_name_id(backend_name), 0)]

    def get_by_name_id(self, backend_name: str) -> int:
        for backend in self.backends:
            if backend.name == backend_name:
                return backend.backend_id
        return -1

    def get_best(self) -> Backend:
        return self.backends[max(self.get_best_id(), 0)]

    def get_best_id(self) -> int:
        for order in self.prefer_order:
            for backend in self.backends:
                if backend.name == order:
                    return backend.backend_id
        return -1
