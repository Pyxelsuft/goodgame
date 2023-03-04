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
        self.window.renderer.fps_font.destroy()
        self.window.renderer.destroy()
        self.window.destroy()
        self.destroy()


class Window(gg.Window):
    def __init__(self, app: any, size: any) -> None:
        super().__init__(app, size=size)
        self.app: App = self.app
        self.emulate_mouse_with_touch = True
        wintheme.set_window_theme(self.get_hwnd(), wintheme.THEME_DARK)
        self.renderer = Renderer(self)

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        if event.button == 0:
            self.renderer.circle_pos = event.pos
            self.renderer.circle_radius = 0
            self.renderer.chunk.play()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym == '1':
            self.renderer.set_vsync(not self.renderer.vsync)


class Renderer(gg.Renderer):
    def __init__(self, window: any) -> None:
        super().__init__(window, vsync=True, backend=gg.BackendManager(window.app).get_best(), force_int=False)
        self.app: App = self.app
        self.window: Window = self.window
        self.window.set_title(f'Good Window [{self.backend.name}]')
        # self.test_tex = self.texture_from_file(self.app.p('example_files', 'img.png'))
        img = Image.open(self.app.p('example_files', 'img.png'))
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
        self.fps_font = gg.TTF(self.app, self.app.p('example_files', 'segoeuib.ttf'), 50)
        self.fps_font.set_kerning(False)
        self.mixer = gg.Mixer(self.app)
        self.music = gg.Music(self.mixer, self.app.p('example_files', 'music.mp3'))
        self.music.set_volume(0.1)
        self.music.play(-1)
        self.chunk = gg.Chunk(self.mixer, self.app.p('example_files', 'click.ogg'))
        self.chunk.set_chunk_volume(0.25)
        self.test_tex = self.texture_from_surface(surf)
        self.circle_pos = (0, 0)
        self.circle_radius = 65.0
        self.counter = 0
        self.window.show()
        self.window.raise_self()

    def update(self) -> None:
        dt = self.app.clock.delta * (10 if self.app.get_key_state('2') else 1)
        self.set_scale([math.sin(self.counter) / 5 + 1 for _ in range(2)])
        # self.fps_font.set_scale([math.sin(self.counter) / 2 + 0.75 for _ in range(2)])
        self.clear()
        self.blit_ex(
            self.test_tex,
            dst_rect=(80, 100),
            angle=math.sin(self.counter * 2) * 10,
            flip_horizontal=(self.counter * 4) % 2 >= 1
        )
        self.draw_rect((0, 255, 0), (100, 100, 100, 100))
        self.draw_rect((255, 0, 0), (100.5, 100.5, 100, 100), 20)
        self.set_scale((1, 1))
        if self.circle_radius <= 64:
            self.draw_circle(
                (0, 255, 255, 255 - self.circle_radius * 4),
                self.circle_pos, self.circle_radius
            )
            self.circle_radius += 150 * dt
        self.blit(self.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.app.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.counter += dt
        self.flip()


if __name__ == '__main__':
    App()
