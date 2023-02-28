import ctypes
from sdl2 import *


# TODO:
#  finish


class AudioDeviceSpec:
    def __init__(self, spec: SDL_AudioSpec = SDL_AudioSpec(0, 0, 0, 0)) -> None:
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
        self.default_playback_info = AudioDeviceSpec()
        self.default_recording_info = AudioDeviceSpec()
        self.get_playback_devices()
        self.get_recording_devices()
        self.get_default_playback_info()
        self.get_default_recording_info()

    def get_default_playback_info(self) -> None:
        name_pointer_type = ctypes.POINTER(ctypes.c_char_p)
        name_pointer = name_pointer_type()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 0)
        self.default_playback_info = AudioDeviceSpec(spec)

    def get_default_recording_info(self) -> None:
        name_pointer_type = ctypes.POINTER(ctypes.c_char_p)
        name_pointer = name_pointer_type()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 1)
        self.default_recording_info = AudioDeviceSpec(spec)

    def get_playback_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(0)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 0))
            self.playback_devices.append(device_name)

    def get_recording_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(1)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 1))
            self.recording_devices.append(device_name)
