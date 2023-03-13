import os
import math
import wintheme  # noqa
os.environ['GG_ENABLE_NUMBA'] = '1'
import goodgame as gg  # noqa


class App(gg.App):
    def __init__(self) -> None:
        super().__init__()
        # self.cwd = os.path.dirname(__file__) or os.getcwd()
        self.init(sdl_flags_list=(
            'video', 'events', 'timer', 'audio', 'joystick', 'game_controller'
        ), mixer_formats=('mp3', 'ogg'))
        self.window = Window(self, (800, 600))
        self.clock = gg.Clock()
        self.clock.reset()
        self.run_loop()

    def on_tick(self) -> None:
        self.poll_events()
        if self.running and self.clock.tick():
            self.window.renderer.update()

    def on_quit(self, event: gg.QuitEvent = None) -> None:
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
        self.set_resizable(True)
        wintheme.set_window_theme(self.get_hwnd(), wintheme.THEME_DARK)
        self.renderer = Renderer(self)

    def on_mouse_down(self, event: gg.MouseButtonEvent) -> None:
        if event.button == 0:
            if event.pos[0] <= 100 and event.pos[1] <= 50:
                self.renderer.set_vsync(not self.renderer.vsync)
            elif event.pos[0] <= 100 and event.pos[1] <= 100:
                self.renderer.draw_rects = not self.renderer.draw_rects
            self.renderer.circle_pos = event.pos
            self.renderer.circle_animation.reset()
            self.renderer.circle_animation.run()
            self.renderer.chunk.play()

    def on_key_down(self, event: gg.KeyboardEvent) -> None:
        if event.sym == '1':
            self.renderer.set_vsync(not self.renderer.vsync)
        elif event.sym == 'Escape':
            self.app.on_quit()


class Renderer(gg.Renderer):
    def __init__(self, window: any) -> None:
        super().__init__(window, vsync=False, backend=gg.BackendManager(window.app).get_best(), force_int=False)
        self.app: App = self.app
        self.window: Window = self.window
        self.window.set_title(f'Good Window [{self.backend.name}]')
        self.cursors = gg.CursorManager(self.app)
        self.mixer = gg.Mixer(self.app)
        self.loader = gg.Loader(
            self.app,
            [
                ('bmp', self.app.p('example_files', 'gradient.bmp')),
                ('image', self.app.p('example_files', 'img.png')),
                ('music', self.app.p('example_files', 'music.mp3')),
                ('sound', self.app.p('example_files', 'click.ogg')),
                ('font', self.app.p('example_files', 'segoeuib.ttf'), 50),
                ('text', self.app.p('example_files', 'goldFont-hd.fnt')),
                ('image', self.app.p('example_files', 'goldFont-hd.png'))
            ]
        )
        self.loader.load = self.load_file
        self.loader.run()
        while not self.loader.finished:  # It's better to use call_on_finish (and create a loading screen)
            continue
        self.fps_font = self.loader.result[4]
        self.fps_font.set_kerning(False)
        self.bg = self.texture_from_surface(self.loader.result[0])
        self.bg.set_scale_mode('linear')
        self.music = self.loader.result[2]
        self.music.set_volume(0.1)
        self.music.play(-1)
        self.chunk = self.loader.result[3]
        self.chunk.set_chunk_volume(0.25)
        self.test_tex = self.texture_from_surface(self.loader.result[1])
        bm_tex = self.texture_from_surface(self.loader.result[6])
        bm_tex.set_scale_mode('linear')
        self.bm_font = gg.BMFont(self, self.loader.result[5], {
            'goldFont-hd.png': bm_tex
        })
        self.circle_pos = (0, 0)
        self.draw_rects = True
        self.scale_animation = gg.Animation(math.pi * 2, repeat=True, enabled=True)
        self.scale_animation.calc = lambda x: math.sin(x) / 5 + 1
        self.rotate_animation = gg.Animation(math.pi * 2, repeat=True, enabled=True)
        self.rotate_animation.calc = lambda x: math.sin(x * 2) * 10
        self.circle_animation = gg.Animation(255 / 4 / 150)
        self.circle_animation.calc = lambda x: x * 150
        self.loader.destroy()
        self.window.show()
        self.window.raise_self()

    def load_file(self, to_load: tuple) -> any:
        if to_load[0] == 'image':
            return self.app.surface_from_file(to_load[1])
        elif to_load[0] == 'bmp':
            return self.app.surface_from_bmp(to_load[1])
        elif to_load[0] == 'music':
            return gg.Music(self.mixer, to_load[1])
        elif to_load[0] == 'sound':
            return gg.Chunk(self.mixer, to_load[1])
        elif to_load[0] == 'font':
            return gg.TTF(self.app, to_load[1], to_load[2])
        elif to_load[0] == 'text':
            return open(to_load[1], 'r', encoding=self.app.encoding).read()

    def update(self) -> None:
        dt = self.app.clock.delta * (10 if self.app.get_key_state('2') else 1)
        self.scale_animation.tick(dt)
        self.rotate_animation.tick(dt)
        self.circle_animation.tick(dt)
        self.set_scale((self.scale_animation.value, self.scale_animation.value))
        self.blit(self.bg)
        self.blit_ex(
            self.test_tex,
            dst_rect=(80, 100),
            angle=self.rotate_animation.value,
            flip_horizontal=False
        )
        if self.draw_rects:
            self.draw_rect((0, 255, 0), (100, 100, 100, 100))
            self.draw_rect((255, 0, 0), (100.5, 100.5, 100, 100), 20)
        bm_tex = self.bm_font.render_lines(
            f'{int(self.scale_animation.value * 100) / 100}\n{int(self.rotate_animation.value)}',
            y_offset=-self.bm_font.common['base'] / 2, wrap_align='center'
        )
        bm_tex.set_scale_mode('linear')
        self.blit(bm_tex, dst_rect=(200, 200))
        self.set_scale((1, 1))
        if self.circle_animation.enabled:
            self.draw_circle(
                (0, 255, 255, 255 - self.circle_animation.value * 4),
                self.circle_pos, self.circle_animation.value
            )
        self.blit(self.texture_from_surface(
            self.fps_font.render_text(f'FPS: {self.app.clock.get_fps()}', (0, 255, 255), blend=True)
        ), dst_rect=(0, self.fps_font.descent))
        self.flip()


if __name__ == '__main__':
    App()
