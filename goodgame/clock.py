from sdl2 import *


class Clock:
    def __init__(self) -> None:
        self.freq = SDL_GetPerformanceFrequency()
        self.delta = 0.0
        self.speed_hack = 1.0
        self.last_tick = 0
        self.fps_limit = 0

    def reset(self) -> None:
        self.last_tick = SDL_GetPerformanceCounter()

    def tick(self) -> bool:
        now = SDL_GetPerformanceCounter()
        if self.fps_limit and self.freq > self.fps_limit * (now - self.last_tick):
            return False
        self.delta = (now - self.last_tick) / self.freq * self.speed_hack
        self.last_tick = now
        return True

    def get_fps(self) -> int:
        try:
            return int(self.speed_hack / self.delta)
        except ZeroDivisionError:
            return self.freq

    def get_fps_float(self) -> float:
        try:
            return self.speed_hack / self.delta
        except ZeroDivisionError:
            return float(self.freq)
