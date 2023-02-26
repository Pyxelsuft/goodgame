import ctypes
from sdl2 import *


class AudioSpec:
    def __init__(self) -> None:
        self.callback: ctypes.CFUNCTYPE = None
        self.channels: int = 0
        self.format: int = 0
        self.freq: int = 0
        self.padding: int = 0
        self.samples: int = 0
        self.silence: int = 0
        self.size: int = 0
        self.userdata: any = None


class AudioManager:
    def __init__(self, app: any) -> None:
        self.app = app
        self.playback_devices = []
        self.recording_devices = []
        self.default_playback_info = AudioSpec()
        self.default_recording_info = AudioSpec()
        self.get_playback_devices()
        self.get_recording_devices()
        self.get_default_playback_info()

    def get_default_playback_info(self) -> None:
        name_pointer_type = ctypes.POINTER(ctypes.c_char_p)
        name_pointer = name_pointer_type()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 0)
        self.default_playback_info.callback = spec.callback
        self.default_playback_info.channels = spec.channels
        self.default_playback_info.format = spec.format
        self.default_playback_info.freq = spec.freq
        self.default_playback_info.padding = spec.padding
        self.default_playback_info.samples = spec.samples
        self.default_playback_info.silence = spec.silence
        self.default_playback_info.size = spec.size
        self.default_playback_info.userdata = spec.userdata

    def get_default_recording_info(self) -> None:
        name_pointer_type = ctypes.POINTER(ctypes.c_char_p)
        name_pointer = name_pointer_type()
        spec = SDL_AudioSpec(0, 0, 0, 0)
        SDL_GetDefaultAudioInfo(name_pointer, spec, 1)
        self.default_recording_info.callback = spec.callback
        self.default_recording_info.channels = spec.channels
        self.default_recording_info.format = spec.format
        self.default_recording_info.freq = spec.freq
        self.default_recording_info.padding = spec.padding
        self.default_recording_info.samples = spec.samples
        self.default_recording_info.silence = spec.silence
        self.default_recording_info.size = spec.size
        self.default_recording_info.userdata = spec.userdata

    def get_playback_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(0)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 0))
            self.playback_devices.append(device_name)

    def get_recording_devices(self) -> None:
        for i in range(SDL_GetNumAudioDevices(1)):
            device_name = self.app.bts(SDL_GetAudioDeviceName(i, 1))
            self.recording_devices.append(device_name)
