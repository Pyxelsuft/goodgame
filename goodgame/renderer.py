import ctypes
from .video import Backend, BackendManager
from .surface import Surface
from .video import PixelFormat
from .texture import Texture
from .sdl import sdl_dir
from sdl2 import *

try:
    from sdl2.sdlimage import *
except:  # noqa
    pass
try:
    from sdl2.sdlgfx import *
except Exception as _err:
    from .sdlgfx import *
    print(f'Failed to import SDL2_gfx [{_err}]. Using extremely slow and unfinished software fallback!')


class Renderer:
    def __init__(
            self,
            window: any,
            backend: Backend = None,
            vsync: bool = False,
            force_int: bool = False
    ) -> None:
        self.destroyed = True
        self.app = window.app
        self.window = window
        self.backend = backend or BackendManager(self.app).get_best()
        self.vsync = vsync
        self.texture = None
        self.format_map = {
            'unknown': SDL_PIXELFORMAT_UNKNOWN,
            'index1lsb': SDL_PIXELFORMAT_INDEX1LSB,
            'index1msb': SDL_PIXELFORMAT_INDEX1MSB,
            'index4lsb': SDL_PIXELFORMAT_INDEX4LSB,
            'index4msb': SDL_PIXELFORMAT_INDEX4MSB,
            'index8': SDL_PIXELFORMAT_INDEX8,
            'rgb332': SDL_PIXELFORMAT_RGB332,
            'rgb444': SDL_PIXELFORMAT_RGB444,
            'rgb555': SDL_PIXELFORMAT_RGB555,
            'bgr555': SDL_PIXELFORMAT_BGR555,
            'argb4444': SDL_PIXELFORMAT_ARGB4444,
            'rgba4444': SDL_PIXELFORMAT_RGBA4444,
            'abgr4444': SDL_PIXELFORMAT_ABGR4444,
            'bgra4444': SDL_PIXELFORMAT_BGRA4444,
            'argb1555': SDL_PIXELFORMAT_ARGB1555,
            'rgba5551': SDL_PIXELFORMAT_RGBA5551,
            'abgr1555': SDL_PIXELFORMAT_ABGR1555,
            'bgra5551': SDL_PIXELFORMAT_BGRA5551,
            'rgb565': SDL_PIXELFORMAT_RGB565,
            'bgr565': SDL_PIXELFORMAT_BGR565,
            'rgb24': SDL_PIXELFORMAT_RGB24,
            'bgr24': SDL_PIXELFORMAT_BGR24,
            'rgb888': SDL_PIXELFORMAT_RGB888,
            'rgbx8888': SDL_PIXELFORMAT_RGBX8888,
            'bgr888': SDL_PIXELFORMAT_BGR888,
            'bgrx8888': SDL_PIXELFORMAT_BGRX8888,
            'argb8888': SDL_PIXELFORMAT_ARGB8888,
            'rgba8888': SDL_PIXELFORMAT_RGBA8888,
            'abgr8888': SDL_PIXELFORMAT_ABGR8888,
            'bgra8888': SDL_PIXELFORMAT_BGRA8888,
            'argb2101010': SDL_PIXELFORMAT_ARGB2101010,
            'rgba32': SDL_PIXELFORMAT_RGBA32,
            'argb32': SDL_PIXELFORMAT_ARGB32,
            'bgra32': SDL_PIXELFORMAT_BGRA32,
            'abgr32': SDL_PIXELFORMAT_ABGR32,
            'yv12': SDL_PIXELFORMAT_YV12,
            'iyuv': SDL_PIXELFORMAT_IYUV,
            'yuy2': SDL_PIXELFORMAT_YUY2,
            'uyvy': SDL_PIXELFORMAT_UYVY,
            'yvyu': SDL_PIXELFORMAT_YVYU,
            'nv12': SDL_PIXELFORMAT_NV12,
            'nv21': SDL_PIXELFORMAT_NV21
        }
        self.access_map = {
            'static': SDL_TEXTUREACCESS_STATIC,
            'target': SDL_TEXTUREACCESS_TARGET,
            'streaming': SDL_TEXTUREACCESS_STREAMING
        }
        if force_int or 'SDL_RenderCopyF' not in sdl_dir:
            self.blit = self.blit_i
            self.blit_ex = self.blit_ex_i
            self.draw_point = self.draw_point_i
            self.draw_points = self.draw_points_i
            self.sdl_draw_rect = self.sdl_draw_rect_i
            self.sdl_draw_rects = self.sdl_draw_rects_i
            self.sdl_fill_rect = self.sdl_fill_rect_i
            self.sdl_fill_rects = self.sdl_fill_rects_i
            self.sdl_draw_line = self.sdl_draw_line_i
            self.sdl_draw_lines = self.sdl_draw_lines_i
        self.renderer = SDL_CreateRenderer(
            window.window,
            self.backend.backend_id,
            SDL_RENDERER_ACCELERATED | SDL_RENDERER_TARGETTEXTURE | (SDL_RENDERER_PRESENTVSYNC if vsync else 0)
        )
        self.integer_scale = bool(SDL_RenderGetIntegerScale(self.renderer))
        self.render_target_supported = bool(SDL_RenderTargetSupported(self.renderer))
        self.destroyed = False
        # TODO:
        #  check out of bounds (check if this handled automatic by sdl)
        #  SDL_RenderReadPixels, SDL_RenderGeometry, SDL_RenderGeometryRaw
        #  Fix Scaling for SDL2_gfx

    def pixel_format_from_str(self, format_str: str) -> PixelFormat:
        return PixelFormat(self.format_map[format_str], self.app)

    def window_to_logical(self, pos: any) -> tuple:
        w_ptr, h_ptr = ctypes.c_float(), ctypes.c_float()
        SDL_RenderWindowToLogical(self.renderer, int(pos[0]), int(pos[1]), w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def logical_to_window(self, pos: any) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_RenderLogicalToWindow(self.renderer, pos[0], pos[1], w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def gt_scale(self) -> tuple:
        scale_x_ptr, scale_y_ptr = ctypes.c_float(), ctypes.c_float()
        SDL_RenderGetScale(self.renderer, scale_x_ptr, scale_y_ptr)
        return scale_x_ptr.value, scale_y_ptr.value

    def set_scale(self, scale: any = (1.0, 1.0)) -> None:
        SDL_RenderSetScale(self.renderer, scale[0], scale[1])

    def is_clip_enabled(self) -> bool:
        return bool(SDL_RenderIsClipEnabled(self.renderer))

    def set_clip_rect(self, clip_rect: any = None) -> None:
        SDL_RenderSetClipRect(
            self.renderer,
            clip_rect and SDL_Rect(int(clip_rect[0]), int(clip_rect[1]), int(clip_rect[2]), int(clip_rect[3]))
        )

    def get_clip_rect(self) -> tuple:
        clip_rect_ptr = SDL_Rect()
        SDL_RenderGetClipRect(self.renderer, clip_rect_ptr)
        return clip_rect_ptr.x, clip_rect_ptr.y, clip_rect_ptr.w, clip_rect_ptr.h

    def set_viewport(self, viewport_rect: any = None) -> None:
        SDL_RenderSetViewport(
            self.renderer,
            viewport_rect and SDL_Rect(int(viewport_rect[0]), int(viewport_rect[1]),
                                       int(viewport_rect[2]), int(viewport_rect[3]))
        )

    def get_viewport(self) -> tuple:
        viewport_ptr = SDL_Rect()
        SDL_RenderGetViewport(self.renderer, viewport_ptr)
        return viewport_ptr.x, viewport_ptr.y, viewport_ptr.w, viewport_ptr.h

    def set_logical_size(self, logical_size: any) -> None:
        SDL_RenderSetLogicalSize(self.renderer, int(logical_size[0]), int(logical_size[1]))

    def get_logical_size(self) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_RenderGetLogicalSize(self.renderer, w_ptr, h_ptr)
        return w_ptr, h_ptr

    def set_integer_scale(self, enabled: bool) -> None:
        self.integer_scale = enabled
        SDL_RenderSetIntegerScale(self.renderer, enabled)

    def set_target(self, target: any = None) -> None:
        SDL_SetRenderTarget(self.renderer, target and target.texture)

    def create_texture(
            self,
            texture_size: any,
            pixel_format: PixelFormat,
            access: str = 'target'
    ) -> Texture:
        return Texture(SDL_CreateTexture(self.renderer, pixel_format.pixel_format, self.access_map[access],
                                         int(texture_size[0]), int(texture_size[1])), self)

    def texture_from_file(self, path: str) -> Texture:
        texture = IMG_LoadTexture(self.renderer, self.app.stb(path))
        if not texture:
            self.app.raise_error(IMG_GetError)
        return Texture(texture, self)

    def blit(self, texture: Texture, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_RenderCopyF(
            self.renderer,
            texture.texture,
            src_rect and SDL_FRect(src_rect[0], src_rect[1], src_rect[2], src_rect[3]),
            dst_rect and (SDL_FRect(dst_rect[0], dst_rect[1], dst_rect[2], dst_rect[3]) if len(dst_rect) > 2 else
                          SDL_FRect(dst_rect[0], dst_rect[1], texture.get_w(), texture.get_h()))
        )

    def blit_i(self, texture: Texture, src_rect: any = None, dst_rect: any = None) -> None:
        SDL_RenderCopy(
            self.renderer,
            texture.texture,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            dst_rect and (SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
                          if len(dst_rect) > 2 else
                          SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), texture.get_w(), texture.get_h()))
        )

    def blit_ex(
            self, texture: Texture, src_rect: any = None, dst_rect: any = None, angle: float = 0.0,
            center: any = None, flip_horizontal: bool = False, flip_vertical: bool = False
    ) -> None:
        SDL_RenderCopyExF(
            self.renderer,
            texture.texture,
            src_rect and SDL_FRect(src_rect[0], src_rect[1], src_rect[2], src_rect[3]),
            dst_rect and (SDL_FRect(dst_rect[0], dst_rect[1], dst_rect[2], dst_rect[3]) if len(dst_rect) > 2 else
                          SDL_FRect(dst_rect[0], dst_rect[1], texture.get_w(), texture.get_h())),
            angle,
            center and SDL_FPoint(center[0], center[1]),
            ((flip_horizontal and SDL_FLIP_HORIZONTAL) | (flip_vertical and SDL_FLIP_VERTICAL)) or SDL_FLIP_NONE
        )

    def blit_ex_i(
            self, texture: Texture, src_rect: any = None, dst_rect: any = None, angle: float = 0.0,
            center: any = None, flip_horizontal: bool = False, flip_vertical: bool = False
    ) -> None:
        SDL_RenderCopyEx(
            self.renderer,
            texture.texture,
            src_rect and SDL_Rect(int(src_rect[0]), int(src_rect[1]), int(src_rect[2]), int(src_rect[3])),
            dst_rect and (SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), int(dst_rect[2]), int(dst_rect[3]))
                          if len(dst_rect) > 2 else
                          SDL_Rect(int(dst_rect[0]), int(dst_rect[1]), texture.get_w(), texture.get_h())),
            angle,
            center and SDL_FPoint(center[0], center[1]),
            ((flip_horizontal and SDL_FLIP_HORIZONTAL) | (flip_vertical and SDL_FLIP_VERTICAL)) or SDL_FLIP_NONE
        )

    def texture_from_surface(self, surf: Surface) -> Texture:
        return Texture(SDL_CreateTextureFromSurface(self.renderer, surf.surface), self)

    def draw_bezier(self, color: any, points: any, steps: float) -> None:
        bezierRGBA(
            self.renderer,
            (ctypes.c_short * len(points))(*(int(point[0]) for point in points)),
            (ctypes.c_short * len(points))(*(int(point[1]) for point in points)),
            len(points), int(steps),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_polygon(self, color: any, points: any, aa: bool = False) -> None:
        (aapolygonRGBA if aa else polygonRGBA)(
            self.renderer,
            (ctypes.c_short * len(points))(*(int(point[0]) for point in points)),
            (ctypes.c_short * len(points))(*(int(point[1]) for point in points)),
            len(points), int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_textured_polygon(self, points: any, surf: Surface, texture_offset: any = (0, 0)) -> None:
        texturedPolygon(
            self.renderer,
            (ctypes.c_short * len(points))(*(int(point[0]) for point in points)),
            (ctypes.c_short * len(points))(*(int(point[1]) for point in points)),
            len(points), surf.surface,
            int(texture_offset[0]), int(texture_offset[1])
        )

    def fill_polygon(self, color: any, points: any) -> None:
        filledPolygonRGBA(
            self.renderer,
            (ctypes.c_short * len(points))(*(int(point[0]) for point in points)),
            (ctypes.c_short * len(points))(*(int(point[1]) for point in points)),
            len(points), int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_trigon(self, color: any, pos1: any, pos2: any, pos3: any, aa: bool = False) -> None:
        (aatrigonRGBA if aa else trigonRGBA)(
            self.renderer,
            int(pos1[0]), int(pos1[1]), int(pos2[0]), int(pos2[1]), int(pos3[0]), int(pos3[1]),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_trigon(self, color: any, pos1: any, pos2: any, pos3: any) -> None:
        filledTrigonRGBA(
            self.renderer,
            int(pos1[0]), int(pos1[1]), int(pos2[0]), int(pos2[1]), int(pos3[0]), int(pos3[1]),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_pie(self, color: any, center: any, rad: float, start: float, end: float) -> None:
        filledPieRGBA(
            self.renderer,
            int(center[0]), int(center[1]), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_pie_tl(self, color: any, pos: any, rad: float, start: float, end: float) -> None:
        filledPieRGBA(
            self.renderer,
            int(pos[0] + rad), int(pos[1] + rad), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_pie(self, color: any, center: any, rad: float, start: float, end: float) -> None:
        pieRGBA(
            self.renderer,
            int(center[0]), int(center[1]), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_pie_tl(self, color: any, pos: any, rad: float, start: float, end: float) -> None:
        pieRGBA(
            self.renderer,
            int(pos[0] + rad), int(pos[1] + rad), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_arc(self, color: any, center: any, rad: float, start: float, end: float) -> None:
        arcRGBA(
            self.renderer,
            int(center[0]), int(center[1]), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_arc_tl(self, color: any, pos: any, rad: float, start: float, end: float) -> None:
        arcRGBA(
            self.renderer,
            int(pos[0] + rad), int(pos[1] + rad), int(rad), int(start), int(end),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_circle(self, color: any, center: any, r: float) -> None:
        filledCircleRGBA(
            self.renderer,
            int(center[0]), int(center[1]), int(r),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_circle_tl(self, color: any, pos: any, r: float) -> None:
        filledCircleRGBA(
            self.renderer,
            int(pos[0] + r), int(pos[1] + r), int(r),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_circle_tl(self, color: any, pos: any, r: float, aa: bool = False) -> None:
        (aacircleRGBA if aa else circleRGBA)(
            self.renderer,
            int(pos[0] + r), int(pos[1] + r), int(r),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_circle(self, color: any, center: any, r: float, aa: bool = False) -> None:
        (aacircleRGBA if aa else circleRGBA)(
            self.renderer,
            int(center[0]), int(center[1]), int(r),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_ellipse(self, color: any, center: any, rx: float, ry: float, aa: bool = False) -> None:
        (aaellipseRGBA if aa else ellipseRGBA)(
            self.renderer,
            int(center[0]), int(center[1]), int(rx), int(ry),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_ellipse_tl(self, color: any, pos: any, rx: float, ry: float, aa: bool = False) -> None:
        (aaellipseRGBA if aa else ellipseRGBA)(
            self.renderer,
            int(pos[0] + rx), int(pos[1] + ry), int(rx), int(ry),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_ellipse(self, color: any, center: any, rx: float, ry: float) -> None:
        filledEllipseRGBA(
            self.renderer,
            int(center[0]), int(center[1]), int(rx), int(ry),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def fill_ellipse_tl(self, color: any, pos: any, rx: float, ry: float) -> None:
        filledEllipseRGBA(
            self.renderer,
            int(pos[0] + rx), int(pos[1] + ry), int(rx), int(ry),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def draw_line(self, color: any, start: any, end: any, width: float = 1.0) -> None:
        if width >= 2:
            return self.gfx_draw_thick_line(color, start, end, width)
        return self.sdl_draw_line(color, start, end)

    def draw_point(self, color: any, point: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawPointF(self.renderer, point[0], point[1])

    def draw_point_i(self, color: any, point: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawPoint(self.renderer, int(point[0]), int(point[1]))

    def draw_points(self, color: any, points: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawPointsF(
            self.renderer,
            (SDL_FPoint * len(points))(*(SDL_FPoint(point[0], point[1]) for point in points)),
            len(points)
        )

    def draw_points_i(self, color: any, points: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawPoints(
            self.renderer,
            (SDL_Point * len(points))(*(SDL_Point(int(point[0]), int(point[1])) for point in points)),
            len(points)
        )

    def draw_rect(self, color: any, draw_rect: any, rad: float = 0.0) -> None:
        if rad >= 1:
            return self.gfx_draw_rounded_rect(color, draw_rect, rad)
        return self.sdl_draw_rect(color, draw_rect)

    def fill_rect(self, color: any, fill_rect: any, rad: float = 0.0) -> None:
        if rad >= 1:
            return self.gfx_fill_rounded_rect(color, fill_rect, rad)
        return self.sdl_fill_rect(color, fill_rect)

    def gfx_draw_rounded_rect(self, color: any, draw_rect: any, rad: float) -> None:
        roundedRectangleRGBA(
            self.renderer,
            int(draw_rect[0]), int(draw_rect[1]), int(draw_rect[0] + draw_rect[2]), int(draw_rect[1] + draw_rect[3]),
            int(rad), int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def gfx_fill_rounded_rect(self, color: any, fill_rect: any, rad: float) -> None:
        roundedBoxRGBA(
            self.renderer,
            int(fill_rect[0]), int(fill_rect[1]), int(fill_rect[0] + fill_rect[2]), int(fill_rect[1] + fill_rect[3]),
            int(rad), int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def sdl_draw_rect(self, color: any, draw_rect: any = None) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawRectF(
            self.renderer,
            draw_rect and SDL_FRect(draw_rect[0], draw_rect[1], draw_rect[2], draw_rect[3])
        )

    def sdl_draw_rect_i(self, color: any, draw_rect: any = None) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawRect(
            self.renderer,
            draw_rect and SDL_Rect(int(draw_rect[0]), int(draw_rect[1]), int(draw_rect[2]), int(draw_rect[3]))
        )

    def sdl_draw_rects(self, color: any, draw_rects: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawRectsF(
            self.renderer,
            (SDL_FRect * len(draw_rects))(*(draw_rect and SDL_FRect(
                draw_rect[0], draw_rect[1], draw_rect[2], draw_rect[3]) for draw_rect in draw_rects)),
            len(draw_rects)
        )

    def sdl_draw_rects_i(self, color: any, draw_rects: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawRects(
            self.renderer,
            (SDL_Rect * len(draw_rects))(*(draw_rect and SDL_Rect(int(
                draw_rect[0]), int(draw_rect[1]), int(draw_rect[2]), int(draw_rect[3])) for draw_rect in draw_rects)),
            len(draw_rects)
        )

    def sdl_fill_rect(self, color: any, fill_rect: any = None) -> None:
        self.set_draw_color(color)
        SDL_RenderFillRectF(
            self.renderer,
            fill_rect and SDL_FRect(fill_rect[0], fill_rect[1], fill_rect[2], fill_rect[3])
        )

    def sdl_fill_rect_i(self, color: any, fill_rect: any = None) -> None:
        self.set_draw_color(color)
        SDL_RenderFillRect(
            self.renderer,
            fill_rect and SDL_Rect(int(fill_rect[0]), int(fill_rect[1]), int(fill_rect[2]), int(fill_rect[3]))
        )

    def sdl_fill_rects(self, color: any, fill_rects: any) -> None:
        self.set_draw_color(color)
        SDL_RenderFillRectsF(
            self.renderer,
            (SDL_FRect * len(fill_rects))(*(fill_rect and SDL_FRect(
                fill_rect[0], fill_rect[1], fill_rect[2], fill_rect[3]) for fill_rect in fill_rects)),
            len(fill_rects)
        )

    def sdl_fill_rects_i(self, color: any, fill_rects: any) -> None:
        self.set_draw_color(color)
        SDL_RenderFillRects(
            self.renderer,
            (SDL_Rect * len(fill_rects))(*(fill_rect and SDL_Rect(int(
                fill_rect[0]), int(fill_rect[1]), int(fill_rect[2]), int(fill_rect[3])) for fill_rect in fill_rects)),
            len(fill_rects)
        )

    def gfx_draw_line(self, color: any, start: any, end: any, aa: bool = False) -> None:
        (aalineRGBA if aa else lineRGBA)(
            self.renderer,
            int(start[0]), int(start[1]), int(end[0]), int(end[1]),
            int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def gfx_draw_thick_line(self, color: any, start: any, end: any, width: float) -> None:
        thickLineRGBA(
            self.renderer,
            int(start[0]), int(start[1]), int(end[0]), int(end[1]),
            int(width), int(color[0]), int(color[1]), int(color[2]), int(color[3]) if len(color) > 3 else 255
        )

    def sdl_draw_line(self, color: any, start: any, end: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawLineF(self.renderer, start[0], start[1], end[0], end[1])

    def sdl_draw_line_i(self, color: any, start: any, end: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawLine(self.renderer, int(start[0]), int(start[1]), int(end[0]), int(end[1]))

    def sdl_draw_lines(self, color: any, points: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawLinesF(
            self.renderer,
            (SDL_FPoint * len(points))(*(SDL_FPoint(point[0], point[1]) for point in points)),
            len(points)
        )

    def sdl_draw_lines_i(self, color: any, points: any) -> None:
        self.set_draw_color(color)
        SDL_RenderDrawLines(
            self.renderer,
            (SDL_Point * len(points))(*(SDL_Point(int(point[0]), int(point[1])) for point in points)),
            len(points)
        )

    def clear(self, color: any = (0, 0, 0, 255)) -> None:
        self.set_draw_color(color)
        SDL_RenderClear(self.renderer)

    def set_draw_color(self, color: any) -> None:
        if len(color) > 3:
            SDL_SetRenderDrawColor(self.renderer, int(color[0]), int(color[1]), int(color[2]), int(color[3]))
            SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_NONE if color[3] >= 255 else SDL_BLENDMODE_BLEND)
        else:
            SDL_SetRenderDrawColor(self.renderer, int(color[0]), int(color[1]), int(color[2]), 255)
            SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_NONE)

    def set_blend_mode(self, mode: str) -> None:
        SDL_SetRenderDrawBlendMode(self.renderer, self.app.blend_map[mode])

    def set_vsync(self, vsync: bool) -> None:
        self.vsync = vsync
        SDL_RenderSetVSync(self.renderer, vsync)

    def flip(self) -> None:
        SDL_RenderPresent(self.renderer)

    def get_output_size(self) -> tuple:
        w_ptr, h_ptr = ctypes.c_int(), ctypes.c_int()
        SDL_GetRendererOutputSize(self.renderer, w_ptr, h_ptr)
        return w_ptr.value, h_ptr.value

    def set_as_target(self) -> None:
        self.renderer.set_target(self)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_DestroyRenderer(self.renderer)
        self.destroyed = True
        self.blit = None
        self.blit_ex = None
        self.draw_point = None
        self.draw_points = None
        self.sdl_draw_rect = None
        self.sdl_draw_rects = None
        self.sdl_fill_rect = None
        self.sdl_fill_rects = None
        self.sdl_draw_line = None
        self.sdl_draw_lines = None
        del self.window
        del self.app
        return False

    def __del__(self) -> None:
        self.destroy()
