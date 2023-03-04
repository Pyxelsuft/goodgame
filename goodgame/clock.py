from sdl2 import *


class Clock:
    def __init__(self) -> None:
        self.freq = SDL_GetPerformanceFrequency()
        self.delta = 0.0
        self.speed_hack = 1.0
        self.last_tick = 0
        self.fps_limit = 0

    @staticmethod
    def get_time() -> float:
        return SDL_GetTicks64() / 1000

    def sleep(self, time: float) -> None:
        wait_for = self.get_time() + time
        while self.get_time() < wait_for:
            continue

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


class Timer:
    def __init__(
            self,
            duration: float,
            repeat: bool = True,
            enabled: bool = False,
            smooth: bool = False
    ) -> None:
        self.duration = duration
        self.repeat = repeat
        self.enabled = enabled
        self.counter = 0.0
        self.triggered = 0
        self.smooth = smooth

    def reset(self) -> None:
        self.triggered = 0
        self.counter = 0.0

    def run(self) -> None:
        self.enabled = True

    def pause(self) -> None:
        self.enabled = False

    def stop(self) -> None:
        self.pause()
        self.reset()

    def tick(self, dt: float) -> None:
        if not self.enabled:
            return
        self.counter += dt
        if self.smooth:
            if self.counter >= self.duration:
                self.counter -= self.duration
                self.triggered += 1
            return
        while self.counter >= self.duration:
            self.counter -= self.duration
            self.triggered += 1


class Animation:
    def __init__(
            self,
            duration: float = 0.0,
            repeat: bool = False,
            enabled: bool = False
    ) -> None:
        self.duration = duration
        self.repeat = repeat
        self.enabled = enabled
        self.counter = 0.0
        self.value: any = None

    def reset(self) -> None:
        self.counter = 0.0

    def run(self) -> None:
        self.enabled = True

    def stop(self) -> None:
        self.pause()
        self.reset()

    def pause(self) -> None:
        self.enabled = False

    def tick(self, dt: float) -> None:
        if not self.enabled:
            return
        self.counter += dt
        if self.duration and self.counter >= self.duration:
            if self.repeat:
                self.counter -= self.duration
            else:
                self.value = self.calc(self.duration)
                return self.stop()
        self.value = self.calc(self.counter)

    @staticmethod
    def calc(counter: float) -> any:
        return counter
