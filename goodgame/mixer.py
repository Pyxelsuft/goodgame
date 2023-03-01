from sdl2 import *
try:
    from sdl2.sdlmixer import *
except:  # noqa
    pass


# TODO:
#  Finish
#  Mix_ModMusicJumpToOrder


class Music:
    def __init__(self, mixer: any, path: str) -> None:
        self.app = mixer.app
        self.path = path
        self.music = Mix_LoadMUS(self.app.stb(path))
        if not self.music:
            self.app.raise_error(Mix_GetError)
        self.type = {
            MUS_NONE: 'NONE',
            MUS_CMD: 'CMD',
            MUS_WAV: 'WAV',
            MUS_MOD: 'MOD',
            MUS_MID: 'MID',
            MUS_OGG: 'OGG',
            MUS_MP3: 'MP3',
            MUS_MP3_MAD_UNUSED: 'MP3_MAD_UNUSED',
            MUS_FLAC: 'FLAC',
            MUS_MODPLUG_UNUSED: 'MODPLUG_UNUSED',
            MUS_OPUS: 'OPUS'
        }.get(Mix_GetMusicType(self.music))
        self.title = self.app.bts(Mix_GetMusicTitle(self.music))
        self.title_tag = self.app.bts(Mix_GetMusicTitleTag(self.music))
        self.artist_tag = self.app.bts(Mix_GetMusicArtistTag(self.music))
        self.album_tag = self.app.bts(Mix_GetMusicAlbumTag(self.music))
        self.copyright_tag = self.app.bts(Mix_GetMusicCopyrightTag(self.music))
        self.duration = Mix_MusicDuration(self.music)
        self.loop_start = Mix_GetMusicLoopStartTime(self.music)
        self.loop_end = Mix_GetMusicLoopEndTime(self.music)
        self.loop_length = Mix_GetMusicLoopLengthTime(self.music)
        self.destroyed = False

    def play(self, loops: int = 0, fade_in: float = 0.0, pos: float = 0.0) -> None:
        if fade_in:
            if pos:
                Mix_FadeInMusicPos(self.music, loops, int(fade_in * 1000), pos)
            else:
                Mix_FadeInMusic(self.music, loops, int(fade_in * 1000))
        else:
            Mix_PlayMusic(self.music, loops)
            if pos:
                self.set_pos(pos)

    @staticmethod
    def set_pos(pos: float) -> None:
        Mix_SetMusicPosition(pos)

    def get_pos(self) -> float:
        return Mix_GetMusicPosition(self.music)

    @staticmethod
    def mod_jump_to_order(order: int) -> None:
        Mix_ModMusicJumpToOrder(order)

    @staticmethod
    def pause() -> None:
        Mix_PauseMusic()

    @staticmethod
    def resume() -> None:
        Mix_ResumeMusic()

    @staticmethod
    def rewind() -> None:
        Mix_RewindMusic()

    @staticmethod
    def is_paused() -> bool:
        return bool(Mix_PausedMusic())

    @staticmethod
    def is_playing() -> bool:
        return bool(Mix_PlayingMusic())

    @staticmethod
    def fading_status() -> str:
        status = Mix_FadingMusic()
        if status == MIX_FADING_OUT:
            return 'out'
        if status == MIX_FADING_IN:
            return 'in'
        return 'no'

    @staticmethod
    def stop() -> None:
        Mix_HaltMusic()

    @staticmethod
    def fade_out(fade_out: float) -> None:
        Mix_FadeOutMusic(int(fade_out * 1000))

    @staticmethod
    def set_volume(volume: float = 1.0) -> None:
        Mix_VolumeMusic(int(volume * MIX_MAX_VOLUME))

    def get_volume(self) -> float:
        return Mix_GetMusicVolume(self.music) / MIX_MAX_VOLUME

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
        self.format = self.format_map[audio_format.lower()]
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
        self.music_decoders = [self.app.bts(Mix_GetMusicDecoder(x)) for x in range(Mix_GetNumMusicDecoders())]
        self.destroyed = False

    def set_sound_fonts(self, paths: tuple) -> None:
        Mix_SetSoundFonts(self.app.stb(';'.join(paths)))

    def set_timidity_config(self, path: str) -> None:
        Mix_SetTimidityCfg(self.app.stb(path))

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
