import array
import ctypes
from sdl2 import *

try:
    from sdl2.sdlmixer import *
except:  # noqa
    pass

try:
    MUS_MP3_MAD_UNUSED = MUS_MP3_MAD_UNUSED
except NameError:
    MUS_MP3_MAD_UNUSED = 7
try:
    MUS_MODPLUG_UNUSED = MUS_MODPLUG_UNUSED
except NameError:
    MUS_MODPLUG_UNUSED = 10
try:
    MUS_OPUS = MUS_OPUS
except NameError:
    MUS_OPUS = 11


# TODO:
#  Effects, etc


class Chunk:
    def __init__(self, mixer: any, path: str = None, wav_data: bytes = None, raw_data: bytes = None) -> None:
        self.destroyed = True
        self.app = mixer.app
        self.path = path
        if raw_data:
            self.buffer = array.array('B', raw_data)
            addr, count = self.buffer.buffer_info()
            self.chunk = Mix_QuickLoad_RAW(ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte)), len(raw_data))
        elif wav_data:
            self.buffer = array.array('B', wav_data)
            addr, count = self.buffer.buffer_info()
            self.chunk = Mix_QuickLoad_WAV(ctypes.cast(addr, ctypes.POINTER(ctypes.c_ubyte)))
        elif path:
            self.chunk = Mix_LoadWAV(self.app.stb(path))
        else:
            raise RuntimeError('No Chunk Audio Data')
        if not self.chunk:
            self.app.raise_error(Mix_GetError)
        self.channel = -1
        self.destroyed = False

    def is_playing(self) -> bool:
        return bool(Mix_Playing(self.channel))

    def is_paused(self) -> bool:
        return bool(Mix_Paused(self.channel))

    def pause(self) -> None:
        Mix_Pause(self.channel)

    def resume(self) -> None:
        Mix_Resume(self.channel)

    def get_fading_status(self) -> str:
        status = Mix_FadingChannel(self.channel)
        if status == MIX_FADING_OUT:
            return 'out'
        if status == MIX_FADING_IN:
            return 'in'
        return 'no'

    def fade_out(self, fade_out: float) -> None:
        Mix_FadeOutChannel(self.channel, int(fade_out * 1000))

    def expire(self, time: float = -1) -> None:
        Mix_ExpireChannel(self.channel, -1 if time == -1 else int(time * 1000))

    def halt(self) -> None:
        Mix_HaltChannel(self.channel)

    def set_chunk_volume(self, volume: float = 1.0) -> None:
        Mix_VolumeChunk(self.chunk, int(volume * MIX_MAX_VOLUME))

    def set_volume(self, volume: float = 1.0) -> None:
        Mix_Volume(self.channel, int(volume * MIX_MAX_VOLUME))

    def play(self, loops: int = 0, channel: int = -1, fade_in: float = 0.0) -> None:
        if fade_in:
            result = Mix_FadeInChannel(channel, self.chunk, loops, int(fade_in * 1000))
        else:
            result = Mix_PlayChannel(channel, self.chunk, loops)
        if result < 0:
            self.app.raise_error(Mix_GetError)
        self.channel = result

    def play_timed(self, loops: int = 0, time: float = -1, channel: int = -1, fade_in: float = 0.0) -> None:
        if fade_in:
            result = Mix_FadeInChannelTimed(
                channel, self.chunk, loops, -1 if time == -1 else int(time * 1000), int(fade_in * 1000)
            )
        else:
            result = Mix_PlayChannelTimed(channel, self.chunk, loops, -1 if time == -1 else int(time * 1000))
        if result < 0:
            self.app.raise_error(Mix_GetError)
        self.channel = result

    def reverse(self, enabled: bool) -> None:
        Mix_SetReverseStereo(self.channel, enabled)

    def set_position(self, angle: float, distance: float) -> None:
        Mix_SetPosition(self.channel, int(angle), int(distance * 255))

    def set_distance(self, distance: float) -> None:
        Mix_SetDistance(self.channel, int(distance * 255))

    def set_panning(self, panning: tuple = (1.0, 1.0)) -> None:
        Mix_SetPanning(self.channel, int(panning[0] * 255), int(panning[1] * 255))

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        Mix_FreeChunk(self.chunk)
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()


class Music:
    def __init__(self, mixer: any, path: str) -> None:
        self.destroyed = True
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
        try:
            self.title = self.app.bts(Mix_GetMusicTitle(self.music))
            self.title_tag = self.app.bts(Mix_GetMusicTitleTag(self.music))
            self.artist_tag = self.app.bts(Mix_GetMusicArtistTag(self.music))
            self.album_tag = self.app.bts(Mix_GetMusicAlbumTag(self.music))
            self.copyright_tag = self.app.bts(Mix_GetMusicCopyrightTag(self.music))
            self.duration = Mix_MusicDuration(self.music)
            self.loop_start = Mix_GetMusicLoopStartTime(self.music)
            self.loop_end = Mix_GetMusicLoopEndTime(self.music)
            self.loop_length = Mix_GetMusicLoopLengthTime(self.music)
        except (RuntimeError, NameError):
            self.title = ''
            self.title_tag = ''
            self.artist_tag = ''
            self.album_tag = ''
            self.copyright_tag = ''
            self.duration = 0.0
            self.loop_start = 0.0
            self.loop_end = 0.0
            self.loop_length = 0.0
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
    def get_fading_status() -> str:
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
        self.destroyed = True
        self.app = app
        try:
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
        except NameError:
            self.format_map = {
                'u8': 8,
                's8': 32776,
                'u16lsb': 16,
                's16lsb': 32784,
                'u16msb': 4112,
                's16msb': 36880,
                'u16': 16,
                's16': 32784,
                's32lsb': 32800,
                's32msb': 36896,
                's32': 32800,
                'f32lsb': 33056,
                'f32msb': 37152,
                'f32': 33056,
                'u16sys': 16,
                's16sys': 32784,
                's32sys': 32800,
                'f32sys': 33056,
                'default': 32784 if SDL_BYTEORDER == SDL_LIL_ENDIAN else 36880
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
        self.channels = Mix_AllocateChannels(-1)
        self.music_decoders = [self.app.bts(Mix_GetMusicDecoder(_x)) for _x in range(Mix_GetNumMusicDecoders())]
        self.chunk_decoders = [self.app.bts(Mix_GetChunkDecoder(_x)) for _x in range(Mix_GetNumChunkDecoders())]
        self.destroyed = False

    @staticmethod
    def set_master_volume(volume: float = 1.0) -> None:
        Mix_MasterVolume(int(volume * MIX_MAX_VOLUME))

    def allocate_channels(self, count: int) -> None:
        self.channels = Mix_AllocateChannels(count)

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
