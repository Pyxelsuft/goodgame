import threading
from sdl2 import *
try:
    from sdl2.sdlimage import *
except:  # noqa
    pass


class Loader:
    def __init__(self, app: any, to_load: any, extra_data: any = None) -> None:
        self.destroyed = True
        self.app = app
        self.extra_data = extra_data
        self.destroyed = False
        self.finished = False
        self.progress = 0.0
        self.counter = 0
        self.total_len = len(to_load)
        self.to_load = list(to_load)
        self.result = []

    def reset(self) -> None:
        self.finished = False
        self.progress = 0.0
        self.counter = 0
        self.total_len = len(self.to_load)
        self.result.clear()

    def run(self) -> None:
        threading.Thread(target=self.thread).start()

    def thread(self) -> None:
        while self.to_load:
            self.result.append(self.load(self.to_load.pop(0)))
            self.counter += 1
            self.progress = self.counter / self.total_len
        self.finished = True

    def load(self, to_load: any) -> any:
        pass
    
    def call_on_finish(self, cb: any) -> None:
        while not self.finished:
            pass
        cb()

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        del self.app
        del self.load
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
