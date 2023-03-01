import os
import math
import sys
import wintheme  # noqa
from PIL import Image  # noqa
import goodgame as gg


class App(gg.App):
    def __init__(self) -> None:
        super().__init__()
        # self.cwd = os.path.dirname(__file__) or os.getcwd()
        self.init(sdl_flags_list=('video', 'events', 'timer', 'audio'), mixer_formats=('mp3', 'ogg'))
        self.window = Window(self, (800, 600))
        self.clock = gg.Clock()
        self.clock.reset()
        self.run_loop()

    def on_tick(self) -> None:
        self.poll_events()
        if self.running and self.clock.tick():
            self.window.renderer.update()

    def on_quit(self, event: gg.QuitEvent) -> None:
        super().on_quit(event)
        self.stop_loop()
        self.window.destroy()
        self.destroy()


class Window(gg.Window):
    def __init__(self, app: any, size: any) -> None:
        super().__init__(app, size=size)
        self.app: App = self.app
        self.emulate_mouse_with_touch = True
        wintheme.set_window_theme(self.get_hwnd(), wintheme.THEME_DARK)
        self.renderer = Renderer(self)


class Renderer(gg.Renderer):
    def __init__(self, window: any) -> None:
        super().__init__(window, vsync=True)
        self.app: App = self.app
        self.window: Window = self.window
        self.window.set_title(f'Good Window [{self.backend.name}]')
        # self.test_tex = self.texture_from_file('e:/other/98bug.png')
        img = Image.open('e:/other/98bug.png')
        pd = img.tobytes()
        surf: gg.Surface = self.app.surface_from_bytes(
            pd,
            img.size,
            24,
            img.size[0] * 3,
            self.app.default_rgb_mask
        )
        surf.blit_scaled(surf, (0, 0, 50, 50), (100, 100, 200, 125))
        self.cursors = gg.CursorManager(self.app)
        self.audio = gg.AudioDeviceManager(self.app)
        self.mixer = gg.Mixer(self.app)
        self.music = gg.Music(self.mixer, 'E:/Music/Terranigma - Underworld.mp3')
        self.music.set_volume(0.0)
        self.music.play(-1)
        self.chunk = gg.Chunk(self.mixer, wav_data=open('e:/music/kisma - we are.wav', 'rb').read())
        self.chunk.set_chunk_volume(0.1)
        self.chunk.play(fade_in=5)
        self.test_tex = self.texture_from_surface(surf)
        self.counter = 0
        self.window.show()
        self.window.raise_self()

    def update(self) -> None:
        dt = self.app.clock.delta
        self.window.set_title(f'FPS: {self.app.clock.get_fps()}')
        self.set_scale([math.sin(self.counter) / 2 + 0.75 for _ in range(2)])
        self.clear()
        self.blit_ex(
            self.test_tex,
            dst_rect=(80, 100),
            angle=math.sin(self.counter) * 10,
            flip_horizontal=(self.counter * 4) % 2 >= 1
        )
        self.draw_rect((0, 255, 0), (100, 100, 100, 100))
        self.draw_rect((255, 0, 0), (100.5, 100.5, 100, 100), 20)
        self.counter += dt
        self.flip()


if __name__ == '__main__':
    App()
