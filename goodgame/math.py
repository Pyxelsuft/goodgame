import os
import sys
import ctypes
from .sdl import sdl_dir
from sdl2 import *

if os.getenv('GG_ENABLE_NUMBA') == '1':
    try:
        import numba
    except Exception as _err:
        from . import numba
        print(f'Failed to import numba [{_err}]. JIT for Math will be disabled!')
else:
    from . import numba


class Math:
    def __init__(self, force_int: bool = False) -> None:
        self.destroyed = True
        if force_int or 'SDL_HasIntersectionF' not in sdl_dir:
            self.has_intersection = self.has_intersection_i
            self.intersect = self.intersect_i
            self.union = self.union_i
            self.intersect_rect_and_line = self.intersect_rect_and_line_i
            self.enclose_points = self.enclose_points_i
        self.destroyed = False
        # TODO
        #  add more functions

    @staticmethod
    def enclose_points(r: any, points: any) -> tuple:
        result = SDL_FRect()
        SDL_EncloseFPoints(
            (SDL_FPoint * len(points))(*(SDL_FPoint(point[0], point[1]) for point in points)),
            len(points),
            SDL_FRect(r[0], r[1], r[2], r[3]),
            result
        )
        return result.x, result.y, result.w, result.h

    @staticmethod
    def enclose_points_i(r: any, points: any) -> tuple:
        result = SDL_Rect()
        SDL_EnclosePoints(
            (SDL_Point * len(points))(*(SDL_Point(int(point[0]), int(point[1])) for point in points)),
            len(points),
            SDL_Rect(int(r[0]), int(r[1]), int(r[2]), int(r[3])),
            result
        )
        return result.x, result.y, result.w, result.h

    @staticmethod
    def intersect_rect_and_line(r: any, start: any, end: any) -> tuple:
        rect_ptr = SDL_FRect(r[0], r[1], r[2], r[3])
        x1_ptr, y1_ptr = ctypes.c_float(start[0]), ctypes.c_float(start[1])
        x2_ptr, y2_ptr = ctypes.c_float(end[0]), ctypes.c_float(end[1])
        SDL_IntersectFRectAndLine(rect_ptr, x1_ptr, y1_ptr, x2_ptr, y2_ptr)
        return x1_ptr.value, y1_ptr.value, x2_ptr.value, y2_ptr.value

    @staticmethod
    def intersect_rect_and_line_i(r: any, start: any, end: any) -> tuple:
        rect_ptr = SDL_Rect(int(r[0]), int(r[1]), int(r[2]), int(r[3]))
        x1_ptr, y1_ptr = ctypes.c_int(int(start[0])), ctypes.c_int(int(start[1]))
        x2_ptr, y2_ptr = ctypes.c_int(int(end[0])), ctypes.c_int(int(end[1]))
        SDL_IntersectRectAndLine(rect_ptr, x1_ptr, y1_ptr, x2_ptr, y2_ptr)
        return x1_ptr.value, y1_ptr.value, x2_ptr.value, y2_ptr.value

    @staticmethod
    def union(a: any, b: any) -> any:
        result = SDL_FRect()
        SDL_UnionFRect(
            SDL_FRect(a[0], a[1], a[2], a[3]),
            SDL_FRect(b[0], b[1], b[2], b[3]),
            result
        )
        return result.x, result.y, result.w, result.h

    @staticmethod
    def union_i(a: any, b: any) -> any:
        result = SDL_Rect()
        SDL_UnionRect(
            SDL_Rect(int(a[0]), int(a[1]), int(a[2]), int(a[3])),
            SDL_Rect(int(b[0]), int(b[1]), int(b[2]), int(b[3])),
            result
        )
        return result.x, result.y, result.w, result.h

    @staticmethod
    def intersect(a: any, b: any) -> any:
        result = SDL_FRect()
        if not SDL_IntersectFRect(
            SDL_FRect(a[0], a[1], a[2], a[3]),
            SDL_FRect(b[0], b[1], b[2], b[3]),
            result
        ):
            return None
        return result.x, result.y, result.w, result.h

    @staticmethod
    def intersect_i(a: any, b: any) -> any:
        result = SDL_Rect()
        if not SDL_IntersectRect(
            SDL_Rect(int(a[0]), int(a[1]), int(a[2]), int(a[3])),
            SDL_Rect(int(b[0]), int(b[1]), int(b[2]), int(b[3])),
            result
        ):
            return None
        return result.x, result.y, result.w, result.h

    @staticmethod
    def has_intersection(a: any, b: any) -> bool:
        return bool(SDL_HasIntersectionF(
            SDL_FRect(a[0], a[1], a[2], a[3]),
            SDL_FRect(b[0], b[1], b[2], b[3])
        ))

    @staticmethod
    def has_intersection_i(a: any, b: any) -> bool:
        return bool(SDL_HasIntersection(
            SDL_Rect(int(a[0]), int(a[1]), int(a[2]), int(a[3])),
            SDL_Rect(int(b[0]), int(b[1]), int(b[2]), int(b[3]))
        ))

    @staticmethod
    @numba.jit(nopython=True, fastmath=True)
    def point_in_rect(r: any, p: any) -> bool:
        return r[0] <= p[0] < r[0] + r[2] and r[1] <= p[1] < r[1] + r[3]

    @staticmethod
    @numba.jit(nopython=True, fastmath=True)
    def rect_empty(r: any) -> bool:
        return r[0] <= 0 or r[1] <= 0

    @staticmethod
    @numba.jit(nopython=True, fastmath=True)
    def rect_equals(a: any, b: any, epsilon: float = sys.float_info.epsilon) -> bool:
        return abs(a[0] - b[0]) <= epsilon and abs(a[1] - b[1]) <= epsilon and\
            abs(a[2] - b[2]) <= epsilon and abs(a[3] - b[3]) <= epsilon

    @staticmethod
    @numba.jit(nopython=True, fastmath=True)
    def rect_equals_i(a: any, b: any) -> bool:
        return int(a[0]) == int(b[0]) and int(a[1]) == int(b[1]) and int(a[2]) == int(b[2]) and int(a[3]) == int(b[3])

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.has_intersection = None
        self.intersect = None
        self.union = None
        self.intersect_rect_and_line = None
        self.enclose_points = None
        self.destroyed = True
        return False
