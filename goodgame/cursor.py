from .surface import Surface
from sdl2 import *


class Cursor:
    def __init__(self, cursor: SDL_Cursor) -> None:
        self.cursor = cursor
        self.destroyed = False

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_FreeCursor(self.cursor)
        self.destroyed = False
        return False

    def __del__(self) -> None:
        self.destroy()


class CursorManager:
    def __init__(self, app: any) -> None:
        self.app = app
        self.default = Cursor(SDL_GetDefaultCursor())
        self.system = {
            'arrow': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_ARROW)),
            'ibeam': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_IBEAM)),
            'wait': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_WAIT)),
            'crosshair': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_CROSSHAIR)),
            'wait_arrow': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_WAITARROW)),
            'size_nw_se': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_SIZENWSE)),
            'size_ne_sw': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_SIZENESW)),
            'size_we': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_SIZEWE)),
            'size_ns': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_SIZENS)),
            'size_all': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_SIZEALL)),
            'no': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_NO)),
            'hand': Cursor(SDL_CreateSystemCursor(SDL_SYSTEM_CURSOR_HAND))
        }
        self.destroyed = False
        # TODO: create cursor, check for errors on system cursors?

    @staticmethod
    def set(cursor: Cursor = None) -> None:
        SDL_SetCursor(cursor and cursor.cursor)

    def from_surface(self, surf: Surface, hot_pos: any = (0, 0)) -> Cursor:
        result = SDL_CreateColorCursor(surf.surface, int(hot_pos[0]), int(hot_pos[1]))
        if not result:
            self.app.raise_error()
        return Cursor(result)

    def get_current(self) -> Cursor:
        result = SDL_GetCursor()
        if not result:
            self.app.raise_error()
        return Cursor(result)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        del self.app
        self.destroyed = False
        return False

    def __del__(self) -> None:
        self.destroy()
