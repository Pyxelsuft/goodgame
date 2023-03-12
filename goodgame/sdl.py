from sdl2 import *


sdl_dir = dir()


class SDLVersion:
    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.num = (self.major << 24) | (self.minor << 8) | (self.patch << 0)

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'

    def __int__(self) -> int:
        return self.num
