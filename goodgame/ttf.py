import ctypes
import struct
from .surface import Surface
from sdl2 import *

try:
    from sdl2.sdlttf import *
except:  # noqa
    pass

try:
    TTF_HINTING_LIGHT_SUBPIXEL = TTF_HINTING_LIGHT_SUBPIXEL
except NameError:
    TTF_HINTING_LIGHT_SUBPIXEL = 4
try:
    TTF_WRAPPED_ALIGN_LEFT = TTF_WRAPPED_ALIGN_LEFT
except NameError:
    TTF_WRAPPED_ALIGN_LEFT = 0
try:
    TTF_WRAPPED_ALIGN_CENTER = TTF_WRAPPED_ALIGN_CENTER
except NameError:
    TTF_WRAPPED_ALIGN_CENTER = 1
try:
    TTF_WRAPPED_ALIGN_RIGHT = TTF_WRAPPED_ALIGN_RIGHT
except NameError:
    TTF_WRAPPED_ALIGN_RIGHT = 2


class TTF:
    def __init__(self, app: any, path: str, size: float, index: int = 0) -> None:
        self.destroyed = True
        self.app = app
        self.size = int(size)
        self.scale = (1.0, 1.0)
        self.encoding = app.encoding
        self.unicode_encoding = 'utf-16'
        self.hint_map = {
            'normal': TTF_HINTING_NORMAL,
            'light': TTF_HINTING_LIGHT,
            'mono': TTF_HINTING_MONO,
            'none': TTF_HINTING_NONE,
            'light_subpixel': TTF_HINTING_LIGHT_SUBPIXEL
        }
        self.r_hint_map = {b: a for a, b in self.hint_map.items()}
        self.font = TTF_OpenFontIndex(app.stb(path), self.size, index)
        if not self.font:
            app.raise_error(TTF_GetError)
        self.normal = False
        self.bold = False
        self.italic = False
        self.underline = False
        self.strike_through = False
        self.outline = TTF_GetFontOutline(self.font)
        self.faces = TTF_FontFaces(self.font)
        self.fixed_width = bool(TTF_FontFaceIsFixedWidth(self.font))
        self.face = app.bts(TTF_FontFaceFamilyName(self.font))
        self.face_style = app.bts(TTF_FontFaceStyleName(self.font))
        try:
            self.sdf = bool(TTF_GetFontSDF(self.font))
        except NameError:
            self.sdf = False
        self.hinting = self.r_hint_map[TTF_GetFontHinting(self.font)]
        self.height = 0
        self.ascent = 0
        self.descent = 0
        self.line_skip = 0
        self.kerning = False
        self.wrapped_align = 'left'
        self.update_styles()
        self.update_vars()
        self.destroyed = False

    def set_sdf(self, sdf: bool) -> None:
        TTF_SetFontSDF(self.font, sdf)

    def set_script(self, script: str) -> None:
        if TTF_SetFontScriptName(self.font, self.app.stb(script)) < 0:
            self.app.raise_error(TTF_GetError)

    def set_direction(self, direction: str = 'ltr') -> None:
        if direction == 'rtl':
            TTF_SetFontDirection(self.font, TTF_DIRECTION_RTL)
        elif direction == 'ttb':
            TTF_SetFontDirection(self.font, TTF_DIRECTION_TTB)
        elif direction == 'btt':
            TTF_SetFontDirection(self.font, TTF_DIRECTION_BTT)
        else:
            TTF_SetFontDirection(self.font, TTF_DIRECTION_LTR)

    def char_info(self, char: str) -> tuple:
        x1_ptr, y1_ptr, x2_ptr, y2_ptr, advance_ptr = ctypes.c_int(), ctypes.c_int(), ctypes.c_int(),\
            ctypes.c_int(), ctypes.c_int()
        TTF_GlyphMetrics32(self.font, ord(char), x1_ptr, y1_ptr, x2_ptr, y2_ptr, advance_ptr)
        return x1_ptr.value, y1_ptr.value, x2_ptr.value, y2_ptr.value, advance_ptr.value

    def has_char(self, char: str) -> bool:
        return bool(TTF_GlyphIsProvided32(self.font, ord(char)))

    def update_vars(self) -> None:
        self.height = TTF_FontHeight(self.font)
        self.ascent = TTF_FontAscent(self.font)
        self.descent = TTF_FontDescent(self.font)
        self.line_skip = TTF_FontLineSkip(self.font)
        self.kerning = bool(TTF_GetFontKerning(self.font))

    def set_kerning(self, kerning: bool) -> None:
        self.kerning = kerning
        TTF_SetFontKerning(self.font, kerning)

    def set_wrapped_align(self, wrapped_align: str) -> None:
        self.wrapped_align = wrapped_align
        if wrapped_align == 'center':
            TTF_SetFontWrappedAlign(self.font, TTF_WRAPPED_ALIGN_CENTER)
        elif wrapped_align == 'right':
            TTF_SetFontWrappedAlign(self.font, TTF_WRAPPED_ALIGN_RIGHT)
        else:
            TTF_SetFontWrappedAlign(self.font, TTF_WRAPPED_ALIGN_LEFT)

    def set_hinting(self, hinting: str = 'normal') -> None:
        self.hinting = hinting
        TTF_SetFontHinting(self.font, self.hint_map[hinting])

    def set_size(self, size: float) -> None:
        self.size = int(size)
        TTF_SetFontSizeDPI(
            self.font, self.size,
            int(72 * self.scale[0]), int(72 * self.scale[1])
        )
        self.update_vars()

    def set_scale(self, scale: any = (1.0, 1.0)) -> None:
        self.scale = scale
        TTF_SetFontSizeDPI(
            self.font, self.size,
            int(72 * self.scale[0]), int(72 * self.scale[1])
        )
        self.update_vars()

    def render_unicode_wrapped(
            self, text: str, fg: any, bg: any = None, blend: bool = False, wrap_length: float = 0.0
    ) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderUNICODE_Shaded_Wrapped(
                    self.font,
                    self.encode_unicode(text),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                    int(wrap_length)
                )
            else:
                surf = TTF_RenderUNICODE_Blended_Wrapped(
                    self.font,
                    self.encode_unicode(text),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    int(wrap_length)
                )
        elif bg:
            surf = TTF_RenderUNICODE_LCD_Wrapped(
                self.font,
                self.encode_unicode(text),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                int(wrap_length)
            )
        else:
            surf = TTF_RenderUNICODE_Solid_Wrapped(
                self.font,
                self.encode_unicode(text),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                int(wrap_length)
            )
        return Surface(surf, self.app)

    def render_unicode(self, text: str, fg: any, bg: any = None, blend: bool = False) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderUNICODE_Shaded(
                    self.font,
                    self.encode_unicode(text),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
                )
            else:
                surf = TTF_RenderUNICODE_Blended(
                    self.font,
                    self.encode_unicode(text),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
                )
        elif bg:
            surf = TTF_RenderUNICODE_LCD(
                self.font,
                self.encode_unicode(text),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
            )
        else:
            surf = TTF_RenderUNICODE_Solid(
                self.font,
                self.encode_unicode(text),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
            )
        return Surface(surf, self.app)

    def render_utf8_wrapped(
            self, text: str, fg: any, bg: any = None, blend: bool = False, wrap_length: float = 0.0
    ) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderUTF8_Shaded_Wrapped(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                    int(wrap_length)
                )
            else:
                surf = TTF_RenderUTF8_Blended_Wrapped(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    int(wrap_length)
                )
        elif bg:
            surf = TTF_RenderUTF8_LCD_Wrapped(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                int(wrap_length)
            )
        else:
            surf = TTF_RenderUTF8_Solid_Wrapped(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                int(wrap_length)
            )
        return Surface(surf, self.app)

    def render_utf8(self, text: str, fg: any, bg: any = None, blend: bool = False) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderUTF8_Shaded(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
                )
            else:
                surf = TTF_RenderUTF8_Blended(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
                )
        elif bg:
            surf = TTF_RenderUTF8_LCD(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
            )
        else:
            surf = TTF_RenderUTF8_Solid(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
            )
        return Surface(surf, self.app)

    def render_text_wrapped(
            self, text: str, fg: any, bg: any = None, blend: bool = False, wrap_length: float = 0.0
    ) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderText_Shaded_Wrapped(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                    int(wrap_length)
                )
            else:
                surf = TTF_RenderText_Blended_Wrapped(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    int(wrap_length)
                )
        elif bg:
            surf = TTF_RenderText_LCD_Wrapped(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255),
                int(wrap_length)
            )
        else:
            surf = TTF_RenderText_Solid_Wrapped(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                int(wrap_length)
            )
        return Surface(surf, self.app)

    def render_text(self, text: str, fg: any, bg: any = None, blend: bool = False) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderText_Shaded(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
                )
            else:
                surf = TTF_RenderText_Blended(
                    self.font,
                    self.app.stb(text, self.encoding),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
                )
        elif bg:
            surf = TTF_RenderText_LCD(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
            )
        else:
            surf = TTF_RenderText_Solid(
                self.font,
                self.app.stb(text, self.encoding),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
            )
        return Surface(surf, self.app)

    def render_char(self, char: str, fg: any, bg: any = None, blend: bool = False) -> Surface:
        if blend:
            if bg:
                surf = TTF_RenderGlyph32_Shaded(
                    self.font,
                    ord(char),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                    SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
                )
            else:
                surf = TTF_RenderGlyph32_Blended(
                    self.font,
                    ord(char),
                    SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
                )
        elif bg:
            surf = TTF_RenderGlyph32_LCD(
                self.font,
                ord(char),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255),
                SDL_Color(int(bg[0]), int(bg[1]), int(bg[2]), int(bg[3]) if len(bg) > 3 else 255)
            )
        else:
            surf = TTF_RenderGlyph32_Solid(
                self.font,
                ord(char),
                SDL_Color(int(fg[0]), int(fg[1]), int(fg[2]), int(fg[3]) if len(fg) > 3 else 255)
            )
        return Surface(surf, self.app)

    def get_utf8_size(self, text: str) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        TTF_SizeUTF8(self.font, self.app.stb(text, self.encoding), w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def get_unicode_size(self, text: str) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        TTF_SizeUNICODE(self.font, self.encode_unicode(text), w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def encode_unicode(self, text: str) -> any:
        strlen = len(text) + 1
        intstr = struct.unpack('H' * strlen, text.encode(self.unicode_encoding))
        intstr = intstr + (0, )
        return (ctypes.c_uint16 * (strlen + 1))(*intstr)

    def set_outline(self, outline: float = 0.0) -> None:
        self.outline = int(outline)
        TTF_SetFontOutline(self.font, self.outline)

    def set_strike_through(self, enabled: bool) -> None:
        self.strike_through = enabled
        self.update_ttf_styles()
        self.update_styles()

    def set_underline(self, enabled: bool) -> None:
        self.underline = enabled
        self.update_ttf_styles()
        self.update_styles()

    def set_italic(self, enabled: bool) -> None:
        self.italic = enabled
        self.update_ttf_styles()
        self.update_styles()

    def set_bold(self, enabled: bool) -> None:
        self.bold = enabled
        self.update_ttf_styles()
        self.update_styles()

    def set_normal(self, enabled: bool) -> None:
        self.normal = enabled
        self.update_ttf_styles()
        self.update_styles()

    def update_ttf_styles(self) -> None:
        styles = 0
        if self.normal:
            styles |= TTF_STYLE_NORMAL
        if self.bold:
            styles |= TTF_STYLE_BOLD
        if self.italic:
            styles |= TTF_STYLE_ITALIC
        if self.underline:
            styles |= TTF_STYLE_UNDERLINE
        if self.strike_through:
            styles |= TTF_STYLE_STRIKETHROUGH
        TTF_SetFontStyle(self.font, styles)

    def update_styles(self) -> None:
        styles = TTF_GetFontStyle(self.font)
        self.normal = bool(styles & TTF_STYLE_NORMAL)
        self.bold = bool(styles & TTF_STYLE_BOLD)
        self.italic = bool(styles & TTF_STYLE_ITALIC)
        self.underline = bool(styles & TTF_STYLE_UNDERLINE)
        self.strike_through = bool(styles & TTF_STYLE_STRIKETHROUGH)

    @staticmethod
    def get_version() -> tuple:
        ver = TTF_Linked_Version().contents
        return ver.major, ver.minor, ver.patch

    @staticmethod
    def get_freetype_version() -> tuple:
        major_ptr, minor_ptr, patch_ptr = ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
        TTF_GetFreeTypeVersion(major_ptr, minor_ptr, patch_ptr)
        return major_ptr.value, minor_ptr.value, patch_ptr.value

    @staticmethod
    def get_harfbuzz_version() -> tuple:
        major_ptr, minor_ptr, patch_ptr = ctypes.c_int(), ctypes.c_int(), ctypes.c_int()
        TTF_GetHarfBuzzVersion(major_ptr, minor_ptr, patch_ptr)
        return major_ptr.value, minor_ptr.value, patch_ptr.value

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        try:
            TTF_CloseFont(self.font)
        except OSError:
            print(f'Failed to close font {self}')
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
