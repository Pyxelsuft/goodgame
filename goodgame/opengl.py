from sdl2 import *


class GLContext:
    def __init__(self, window: any, context: int) -> None:
        self.destroyed = True
        self.window = window
        self.context = context
        self.attr_map = {
            'context_major_version': SDL_GL_CONTEXT_MAJOR_VERSION,
            'context_minor_version': SDL_GL_CONTEXT_MINOR_VERSION,
            'context_profile_mask': SDL_GL_CONTEXT_PROFILE_MASK,
            'context_profile_core': SDL_GL_CONTEXT_PROFILE_CORE
        }
        self.destroyed = False

    def swap_window(self) -> None:
        SDL_GL_SwapWindow(self.window.window)

    def set_attribute(self, attr: str, val: int) -> None:
        SDL_GL_SetAttribute(self.context, self.attr_map[attr], val)

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_GL_DeleteContext(self.context)
        del self.window
        self.destroyed = True
        return False

    def __int__(self) -> int:
        return self.context

    def __del__(self) -> None:
        self.destroy()
