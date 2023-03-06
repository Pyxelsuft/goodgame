import ctypes
from .video import PixelFormat
from sdl2 import *

try:
    from sdl2.sdlimage import *
except:  # noqa
    pass

try:
    IMG_Animation = IMG_Animation
except NameError:
    IMG_Animation = any


class Surface:
    def __init__(self, surf: SDL_Surface, app: any) -> None:
        # TODO: lazy SDL_ConvertPixels
        self.destroyed = True
        if not surf:
            app.raise_error()
        self.app = app
        self.surface = surf
        self.format = PixelFormat(surf.contents.format.contents.format, app)
        self.w, self.h = surf.contents.w, surf.contents.h
        self.size = self.w, self.h
        self.clip_rect = (
            surf.contents.clip_rect.x, surf.contents.clip_rect.y,
            surf.contents.clip_rect.w, surf.contents.clip_rect.h
        )
        self.destroyed = False
        self.color_mod = self.get_color_mod()
        self.color_key = self.get_color_key()
        self.alpha_mod = self.get_alpha_mod()
        self.blend_mode = self.get_blend_mode_int()
        try:
            self.has_color_key = bool(SDL_HasColorKey(self.surface))
        except NameError:
            self.has_color_key = False
        try:
            self.has_rle = bool(SDL_HasSurfaceRLE(self.surface))
        except NameError:
            self.has_rle = False
        self.must_lock = self.has_rle

    def update_blend_mode_by_alpha(self) -> None:
        SDL_SetSurfaceBlendMode(self.surface, SDL_BLENDMODE_NONE if self.alpha_mod >= 255 else SDL_BLENDMODE_NONE)

    def get_blend_mode(self) -> str:
        return self.app.r_blend_map[self.blend_mode]

    def set_blend_mode(self, blend_mode: str) -> None:
        self.set_blend_mode_int(self.app.blend_map[blend_mode])

    def get_blend_mode_int(self) -> int:
        try:
            blend_mode_ptr = ctypes.c_long()
            SDL_GetSurfaceBlendMode(self.surface, blend_mode_ptr)
        except ctypes.ArgumentError:
            blend_mode_ptr = ctypes.c_int()
            SDL_GetSurfaceBlendMode(self.surface, blend_mode_ptr)
        return blend_mode_ptr.value

    def set_blend_mode_int(self, blend_mode: int) -> None:
        SDL_SetSurfaceBlendMode(self.surface, blend_mode)
        self.blend_mode = self.get_blend_mode_int()

    def set_clip_rect(self, clip_rect: any) -> None:
        SDL_SetClipRect(self.surface, SDL_Rect(
            int(clip_rect[0]), int(clip_rect[1]), int(clip_rect[2]), int(clip_rect[3])
        ))
        self.clip_rect = (
            self.surface.contents.clip_rect.x, self.surface.contents.clip_rect.y,
            self.surface.contents.clip_rect.w, self.surface.contents.clip_rect.h
        )

    def lock(self) -> None:
        SDL_LockSurface(self.surface)

    def unlock(self) -> None:
        SDL_UnlockSurface(self.surface)

    def set_rle(self, enabled: bool) -> None:
        SDL_SetSurfaceRLE(self.surface, enabled)
        try:
            self.has_rle = bool(SDL_HasSurfaceRLE(self.surface))
        except NameError:
            self.has_rle = enabled
        self.must_lock = self.has_rle

    def map_rgba(self, color: any) -> int:
        return SDL_MapRGBA(self.surface.contents.format, int(color[0]), int(color[1]), int(color[2]), int(color[3]))

    def map_rgb(self, color: any) -> int:
        return SDL_MapRGB(self.surface.contents.format, int(color[0]), int(color[1]), int(color[2]))

    def set_alpha_mod(self, alpha_mod: int = 0) -> None:
        SDL_SetSurfaceAlphaMod(self.surface, alpha_mod)
        self.alpha_mod = self.get_alpha_mod()
        self.update_blend_mode_by_alpha()

    def get_alpha_mod(self) -> int:
        try:
            alpha_mod_ptr = ctypes.c_ulong()
            SDL_GetColorKey(self.surface, alpha_mod_ptr)
        except ctypes.ArgumentError:
            alpha_mod_ptr = ctypes.c_uint()
            SDL_GetColorKey(self.surface, alpha_mod_ptr)
        return alpha_mod_ptr.value

    def set_color_key(self, enabled: bool, color_key: int = 0) -> None:
        if enabled:
            self.color_key = color_key
        SDL_SetColorKey(self.surface, enabled, color_key)
        try:
            self.has_color_key = bool(SDL_HasColorKey(self.surface))
        except NameError:
            self.has_color_key = enabled

    def get_color_key(self) -> int:
        try:
            key_ptr = ctypes.c_ulong()
            SDL_GetColorKey(self.surface, key_ptr)
        except ctypes.ArgumentError:
            key_ptr = ctypes.c_uint()
            SDL_GetColorKey(self.surface, key_ptr)
        return key_ptr.value

    def set_color_mod(self, color_mod: any) -> None:
        SDL_SetSurfaceColorMod(self.surface, int(color_mod[0]), int(color_mod[1]), int(color_mod[2]))
        self.color_mod = self.get_color_mod()

    def get_color_mod(self) -> tuple:
        r_ptr, g_ptr, b_ptr = ctypes.c_ubyte(), ctypes.c_ubyte(), ctypes.c_ubyte()
        SDL_GetSurfaceColorMod(self.surface, r_ptr, g_ptr, b_ptr)
        return r_ptr.value, g_ptr.value, b_ptr.value

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_FreeSurface(self.surface)
        self.destroyed = True
        del self.app
        return False

    def copy(self) -> any:
        return Surface(SDL_DuplicateSurface(self.surface), self.app)

    def convert(self, pixel_format: PixelFormat) -> any:
        return Surface(SDL_ConvertSurfaceFormat(self.surface, pixel_format.pixel_format, 0), self.app)

    def fill_rect(self, color: any, fill_rect: any) -> None:
        SDL_FillRect(
            self.surface,
            fill_rect and SDL_Rect(int(fill_rect[0]), int(fill_rect[1]), int(fill_rect[2]), int(fill_rect[3])),
            self.map_rgba(color) if len(color) > 3 else self.map_rgb(color)
        )

    def fill_rects(self, color: any, fill_rects: any) -> None:
        SDL_FillRects(
            self.surface,
            (SDL_Rect * len(fill_rects))(*(fill_rect and SDL_Rect(
                int(fill_rect[0]), int(fill_rect[1]), int(fill_rect[2]), int(fill_rect[3])
            ) for fill_rect in fill_rects)),
            len(fill_rects),
            self.map_rgba(color) if len(color) > 3 else self.map_rgb(color)
        )

    def blit(self, src: any, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_BlitSurface(
            src.surface,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            self.surface,
            dst_rect and SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
        )

    def blit_to(self, dst: any, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_BlitSurface(
            self.surface,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            dst.surface,
            dst_rect and SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
        )

    def blit_scaled(self, src: any, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_BlitScaled(
            src.surface,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            self.surface,
            dst_rect and SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
        )

    def blit_scaled_to(self, dst: any, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_BlitScaled(
            self.surface,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            dst.surface,
            dst_rect and SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
        )

    def save_to_bmp(self, path: str) -> None:
        if SDL_SaveBMP(self.surface, self.app.stb(path)) < 0:
            self.app.raise_error()

    def save_to_png(self, path: str) -> None:
        if IMG_SavePNG(self.surface, self.app.stb(path)) < 0:
            self.app.raise_error(IMG_GetError)

    def save_to_jpg(self, path: str, quality: float = 1.0) -> None:
        if IMG_SaveJPG(self.surface, self.app.stb(path), int(quality * 100)) < 0:
            self.app.raise_error(IMG_GetError)

    def __del__(self) -> None:
        self.destroy()


class SurfaceAnimation:
    def __init__(self, animation: IMG_Animation, app: any) -> None:
        self.destroyed = True
        self.animation = animation
        self.size = animation.w, animation.h
        self.surfaces = tuple(Surface(animation.frames[_x], app) for _x in range(animation.count))
        self.delays = tuple(animation.delays[_x] for _x in range(animation.count))
        self.destroyed = False

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        IMG_FreeAnimation(self.animation)
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
