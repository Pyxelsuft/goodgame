from sdl2 import *


sdl_dir = dir()


class SDLVersion:
    def __init__(self, ver: SDL_version) -> None:
        self.ver = ver
        self.major = ver.major
        self.minor = ver.minor
        self.patch = ver.patch
        self.num = (self.major << 24) | (self.minor << 8) | (self.patch << 0)

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'

    def __int__(self) -> int:
        return self.num
