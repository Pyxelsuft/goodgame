import ctypes
from sdl2 import *


class AudioSpec:
    def __init__(
            self,
            spec: SDL_AudioSpec = SDL_AudioSpec(0, 0, 0, 0),
            is_capture: bool = False,
            device_name: str = None
    ) -> None:
        self.spec = spec
        self.is_capture = is_capture
        self.device_name = device_name
        self.callback = spec.callback
        self.channels = spec.channels
        self.format = spec.format
        self.freq = spec.freq
        self.padding = spec.padding
        self.samples = spec.samples
        self.silence = spec.silence
        self.size = spec.size
        self.userdata = spec.userdata

    def as_spec(self) -> SDL_AudioSpec:
        spec = SDL_AudioSpec(self.freq, self.format, self.channels, self.samples)
        spec.callback = self.callback
        spec.channels = self.channels
        spec.format = self.format
        spec.freq = self.freq
        spec.padding = self.padding
        spec.samples = self.samples
        spec.silence = self.silence
        spec.size = self.size
        spec.userdata = self.userdata
        return spec


class WAV:
    def __init__(self, spec: AudioSpec, buf_ptr: any, size: int) -> None:
        self.destroyed = True
        self.spec = spec
        self.buf_ptr = buf_ptr
        self.size = size
        self.destroyed = False

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_FreeWAV(self.buf_ptr)
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()


class AudioDevice:
    def __init__(self, app: any, device_id: int, spec: AudioSpec) -> None:
        self.destroyed = True
        self.app = app
        self.id = device_id
        self.spec = spec
        self.destroyed = False
        # TODO:
        #  finish (but why we need it when Mixer exists?)

    def queue(self, data: any, size: int) -> None:
        if SDL_QueueAudio(self.id, data, size) < 0:
            self.app.raise_error()

    def lock(self) -> None:
        SDL_LockAudioDevice(self.id)

    def unlock(self) -> None:
        SDL_UnlockAudioDevice(self.id)

    def pause(self) -> None:
        SDL_PauseAudioDevice(self.id, 1)

    def resume(self) -> None:
        SDL_PauseAudioDevice(self.id, 0)

    def get_status(self) -> str:
        status = SDL_GetAudioDeviceStatus(self.id)
        if status == SDL_AUDIO_PLAYING:
            return 'playing'
        elif status == SDL_AUDIO_PAUSED:
            return 'paused'
        else:
            return 'stopped'

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        SDL_CloseAudioDevice(self.id)
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()


class AudioDeviceManager:
    def __init__(self, app: any) -> None:
        self.app = app
        self.current_driver = app.bts(SDL_GetCurrentAudioDriver())
        self.playback_devices = []
        self.recording_devices = []
        try:
            self.default_playback_info = self.get_default_playback_info()
            self.default_recording_info = self.get_default_recording_info()
        except (RuntimeError, NameError):
            self.default_playback_info = AudioSpec(is_capture=False)
            self.default_recording_info = AudioSpec(is_capture=True)
        self.get_playback_devices()
        self.get_recording_devices()

    def load_wav(self, path: str) -> WAV:
        spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
        buf_ptr = ctypes.POINTER(ctypes.c_uint8)()
        len_ptr = ctypes.c_uint32()
        if not SDL_LoadWAV(self.app.stb(path), spec_ptr, buf_ptr, len_ptr):
            self.app.raise_error()
        return WAV(AudioSpec(spec_ptr, False), buf_ptr, len_ptr.value)

    def open_device(self, spec: AudioSpec) -> AudioDevice:
        spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
        device_id = SDL_OpenAudioDevice(
            spec.device_name and self.app.stb(spec.device_name),
            spec.is_capture,
            spec.as_spec(),
            spec_ptr,
            SDL_AUDIO_ALLOW_ANY_CHANGE
        )
        if device_id == 0:
            self.app.raise_error()
        return AudioDevice(self.app, device_id, AudioSpec(spec_ptr, spec.is_capture, spec.device_name))

    def get_default_playback_info(self) -> AudioSpec:
        name_ptr = ctypes.c_char_p()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_ptr, spec, 0)
        return AudioSpec(spec, False, self.app.bts(name_ptr.value or b''))

    def get_default_recording_info(self) -> AudioSpec:
        name_ptr = ctypes.c_char_p()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_ptr, spec, 1)
        return AudioSpec(spec, True, self.app.bts(name_ptr.value or b''))

    def get_playback_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(0)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 0) or b'')
            spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
            try:
                SDL_GetAudioDeviceSpec(i, 0, spec_ptr)
            except NameError:
                pass
            self.playback_devices.append(AudioSpec(spec_ptr, False, device_name))

    def get_recording_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(1)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 1) or b'')
            spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
            try:
                SDL_GetAudioDeviceSpec(i, 1, spec_ptr)
            except NameError:
                pass
            self.playback_devices.append(AudioSpec(spec_ptr, True, device_name))
