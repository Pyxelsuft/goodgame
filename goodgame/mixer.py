from sdl2 import *
try:
    from sdl2.sdlmixer import *
except:  # noqa
    pass


# TODO:
#  Finish


class Music:
    def __init__(self, mixer: any, path: str) -> None:
        self.app = mixer.app
        self.path = path
        self.music = Mix_LoadMUS(self.app.stb(path))
        if not self.music:
            self.app.raise_error(Mix_GetError)
        self.destroyed = False

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        Mix_FreeMusic(self.music)
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()


class Mixer:
    def __init__(
            self,
            app: any,
            freq: float = float(MIX_DEFAULT_FREQUENCY),
            audio_format: str = 'default',
            num_channels: int = MIX_DEFAULT_CHANNELS,
            chunk_size: int = 2048,
            open_device: bool = True,
            device: str = None
    ) -> None:
        self.app = app
        self.format_map = {
            'u8': AUDIO_U8,
            's8': AUDIO_S8,
            'u16lsb': AUDIO_U16LSB,
            's16lsb': AUDIO_S16LSB,
            'u16msb': AUDIO_U16MSB,
            's16msb': AUDIO_S16MSB,
            'u16': AUDIO_U16,
            's16': AUDIO_S16,
            's32lsb': AUDIO_S32LSB,
            's32msb': AUDIO_S32MSB,
            's32': AUDIO_S32,
            'f32lsb': AUDIO_F32LSB,
            'f32msb': AUDIO_F32MSB,
            'f32': AUDIO_F32,
            'u16sys': AUDIO_U16SYS,
            's16sys': AUDIO_S16SYS,
            's32sys': AUDIO_S32SYS,
            'f32sys': AUDIO_F32SYS,
            'default': MIX_DEFAULT_FORMAT
        }
        self.freq = int(freq)
        self.format = self.format_map[audio_format]
        self.channels = num_channels
        self.chunk_size = chunk_size
        self.version = self.get_version()
        self.device_opened = open_device
        if device and open_device:
            if Mix_OpenAudioDevice(
                    self.freq, self.format, self.channels, self.chunk_size, app.stb(device), SDL_AUDIO_ALLOW_ANY_CHANGE
            ) < 0:
                app.raise_error(Mix_GetError)
        elif open_device:
            if Mix_OpenAudio(self.freq, self.format, self.channels, self.chunk_size) < 0:
                app.raise_error(Mix_GetError)
        self.destroyed = False

    @staticmethod
    def get_version() -> tuple:
        ver = Mix_Linked_Version().contents
        return ver.major, ver.minor, ver.patch

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        if self.device_opened:
            self.device_opened = False
            Mix_CloseAudio()
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
