import ctypes
from sdl2 import *


# TODO:
#  finish (but why we need it when SDL_mixer exists?)


class AudioSpec:
    def __init__(
            self,
            spec: SDL_AudioSpec = SDL_AudioSpec(0, 0, 0, 0),
            is_capture: bool = False,
            device_name: str = ''
    ) -> None:
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


class AudioDeviceManager:
    def __init__(self, app: any) -> None:
        self.app = app
        self.current_driver = app.bts(SDL_GetCurrentAudioDriver())
        self.playback_devices = []
        self.recording_devices = []
        self.default_playback_info = self.get_default_playback_info()
        self.default_recording_info = self.get_default_recording_info()
        self.get_playback_devices()
        self.get_recording_devices()

    def get_default_playback_info(self) -> AudioSpec:
        name_pointer = ctypes.c_char_p()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 0)
        return AudioSpec(spec, False, self.app.bts(name_pointer.value))

    def get_default_recording_info(self) -> AudioSpec:
        name_pointer = ctypes.c_char_p()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 1)
        return AudioSpec(spec, True, self.app.bts(name_pointer.value))

    def get_playback_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(0)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 0))
            spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
            SDL_GetAudioDeviceSpec(i, 0, spec_ptr)
            self.playback_devices.append(AudioSpec(spec_ptr, False, device_name))

    def get_recording_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(1)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 1))
            spec_ptr = SDL_AudioSpec(0, 0, 0, 0)
            SDL_GetAudioDeviceSpec(i, 1, spec_ptr)
            self.playback_devices.append(AudioSpec(spec_ptr, True, device_name))
