import ctypes
from .video import PixelFormat
from sdl2 import *


class Texture:
    def __init__(self, texture: SDL_Texture, renderer: any) -> None:
        self.destroyed = True
        if not texture:
            renderer.app.raise_error()
        self.app = renderer.app
        self.texture = texture
        self.scale_mode = self.get_scale_mode()
        self.color_mod = self.get_color_mod()
        self.alpha_mod = self.get_alpha_mod()
        self.blend_mode = self.get_blend_mode_int()
        self.destroyed = False

    def get_scale_mode(self) -> str:
        scale_mode_ptr = ctypes.c_int()
        try:
            SDL_GetTextureScaleMode(self.texture, scale_mode_ptr)
        except NameError:
            return 'best'
        if scale_mode_ptr.value == SDL_ScaleModeBest:
            return 'best'
        if scale_mode_ptr.value == SDL_ScaleModeNearest:
            return 'nearest'
        if scale_mode_ptr.value == SDL_ScaleModeLinear:
            return 'linear'
        return 'unknown'

    def set_scale_mode(self, scale_mode: str) -> None:
        if scale_mode == 'best':
            SDL_SetTextureScaleMode(self.texture, SDL_ScaleModeBest)
        elif scale_mode == 'nearest':
            SDL_SetTextureScaleMode(self.texture, SDL_ScaleModeNearest)
        elif scale_mode == 'linear':
            SDL_SetTextureScaleMode(self.texture, SDL_ScaleModeLinear)
        self.scale_mode = self.get_scale_mode()

    def set_color_mod(self, color_mod: any) -> None:
        SDL_SetTextureColorMod(self.texture, int(color_mod[0]), int(color_mod[1]), int(color_mod[2]))
        self.color_mod = self.get_color_mod()

    def get_color_mod(self) -> tuple:
        r_ptr, g_ptr, b_ptr = ctypes.c_ubyte(), ctypes.c_ubyte(), ctypes.c_ubyte()
        SDL_GetTextureColorMod(self.texture, r_ptr, g_ptr, b_ptr)
        return r_ptr.value, g_ptr.value, b_ptr.value

    def update_blend_mode_by_alpha(self) -> None:
        SDL_SetTextureBlendMode(self.texture, SDL_BLENDMODE_NONE if self.alpha_mod >= 255 else SDL_BLENDMODE_NONE)

    def get_blend_mode(self) -> str:
        return self.app.r_blend_map[self.blend_mode]

    def set_blend_mode(self, blend_mode: str) -> None:
        self.set_blend_mode_int(self.app.blend_map[blend_mode])

    def get_blend_mode_int(self) -> int:
        try:
            blend_mode_ptr = ctypes.c_long()
            SDL_GetTextureBlendMode(self.texture, blend_mode_ptr)
        except ctypes.ArgumentError:
            blend_mode_ptr = ctypes.c_int()
            SDL_GetTextureBlendMode(self.texture, blend_mode_ptr)
        return blend_mode_ptr.value

    def set_blend_mode_int(self, blend_mode: int) -> None:
        SDL_SetTextureBlendMode(self.texture, blend_mode)
        self.blend_mode = self.get_blend_mode_int()

    def get_alpha_mod(self) -> int:
        alpha_ptr = ctypes.c_ubyte()
        SDL_GetTextureAlphaMod(self.texture, alpha_ptr)
        return alpha_ptr.value

    def set_alpha_mod(self, alpha_mod: float) -> None:
        SDL_SetTextureAlphaMod(self.texture, int(alpha_mod))
        self.alpha_mod = self.get_alpha_mod()
        self.update_blend_mode_by_alpha()

    def get_size(self) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_QueryTexture(self.texture, None, None, w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def get_w(self) -> int:
        w_ptr = ctypes.c_int()
        SDL_QueryTexture(self.texture, None, None, w_ptr, None)
        return w_ptr.value

    def get_h(self) -> int:
        h_ptr = ctypes.c_int()
        SDL_QueryTexture(self.texture, None, None, None, h_ptr)
        return h_ptr.value

    def get_access_type(self) -> str:
        access_ptr = ctypes.c_int()
        SDL_QueryTexture(self.texture, None, access_ptr, None, None)
        if access_ptr.value == SDL_TEXTUREACCESS_STREAMING:
            return 'streaming'
        if access_ptr.value == SDL_TEXTUREACCESS_TARGET:
            return 'target'
        if access_ptr.value == SDL_TEXTUREACCESS_STATIC:
            return 'static'
        return 'none'

    def get_format(self) -> PixelFormat:
        format_ptr = ctypes.c_uint32()
        SDL_QueryTexture(self.texture, format_ptr, None, None, None)
        return PixelFormat(format_ptr.value, self.app)

    def lock(self) -> None:
        SDL_LockTexture(self.texture)

    def unlock(self) -> None:
        SDL_UnlockTexture(self.texture)

    def update(self, data: any, pitch: int, update_rect: any = None) -> None:
        SDL_UpdateTexture(
            self.texture,
            update_rect and SDL_Rect(int(update_rect[0]), int(update_rect[1]),
                                     int(update_rect[2]), int(update_rect[3])),
            data,
            pitch
        )

    def update_yuv(
            self, y_plane: any, y_pitch: int, u_plane: any, u_pitch: int,
            v_plane: any, v_pitch: int, update_rect: any = None
    ) -> None:
        SDL_UpdateYUVTexture(
            self.texture,
            update_rect and SDL_Rect(int(update_rect[0]), int(update_rect[1]),
                                     int(update_rect[2]), int(update_rect[3])),
            y_plane, y_pitch, u_plane, u_pitch, v_plane, v_pitch
        )

    def update_nv(self, y_plane: any, y_pitch: int, uv_plane: any, uv_pitch: int, update_rect: any = None) -> None:
        SDL_UpdateNVTexture(
            self.texture,
            update_rect and SDL_Rect(int(update_rect[0]), int(update_rect[1]),
                                     int(update_rect[2]), int(update_rect[3])),
            y_plane, y_pitch, uv_plane, uv_pitch
        )

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_DestroyTexture(self.texture)
        self.destroyed = True
        del self.app
        return False

    def __del__(self) -> None:
        self.destroy()
