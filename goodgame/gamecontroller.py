import ctypes
from sdl2 import *


class GameController:
    def __init__(self, app: any, index: int) -> None:
        self.app = app
        self.destroyed = True
        self.index = index
        self.name = app.bts(SDL_GameControllerNameForIndex(index))
        try:
            self.path = app.bts(SDL_GameControllerPathForIndex(index))
        except NameError:
            self.path = ''
        try:
            self.type = {
                SDL_CONTROLLER_TYPE_UNKNOWN: 'unknown',
                SDL_CONTROLLER_TYPE_XBOX360: 'xbox_360',
                SDL_CONTROLLER_TYPE_XBOXONE: 'xbox_one',
                SDL_CONTROLLER_TYPE_PS3: 'ps3',
                SDL_CONTROLLER_TYPE_PS4: 'ps4',
                SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_PRO: 'nintendo_switch_pro',
                SDL_CONTROLLER_TYPE_VIRTUAL: 'virtual',
                SDL_CONTROLLER_TYPE_PS5: 'ps5',
                SDL_CONTROLLER_TYPE_AMAZON_LUNA: 'amazon_luna',
                SDL_CONTROLLER_TYPE_GOOGLE_STADIA: 'google_stadia',
                SDL_CONTROLLER_TYPE_NVIDIA_SHIELD: 'nvidia_shield',
                SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_LEFT: 'nintendo_switch_joy_con_left',
                SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT: 'nintendo_switch_joy_con_right',
                SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_PAIR: 'nintendo_switch_joy_con_right'
            }.get(SDL_GameControllerTypeForIndex(index))
        except NameError:
            self.type = 'unknown'
        self.opened = False
        self.player_index = -1
        self.vendor = 0
        self.product = 0
        self.product_version = 0
        self.firmware_version = 0
        self.serial = b''
        self.controller = SDL_GameController()
        self.destroyed = False
        # TODO:
        #  finish

    def add_mappings_from_file(self, path: str) -> None:
        SDL_GameControllerAddMappingsFromFile(self.app.stb(path))

    def add_mapping(self, mapping: str) -> None:
        SDL_GameControllerAddMapping(self.app.stb(mapping))

    def is_attached(self) -> bool:
        return bool(SDL_GameControllerGetAttached(self.controller))

    def set_player_index(self, player_index: int = -1) -> None:
        self.player_index = player_index
        SDL_GameControllerSetPlayerIndex(self.controller, player_index)

    def open(self) -> None:
        self.controller = SDL_GameControllerOpen(self.index)
        self.vendor = SDL_GameControllerGetVendor(self.controller)
        self.product = SDL_GameControllerGetProduct(self.controller)
        self.product_version = SDL_GameControllerGetProductVersion(self.controller)
        try:
            self.firmware_version = SDL_GameControllerGetFirmwareVersion(self.controller)
        except NameError:
            pass
        try:
            self.serial = SDL_GameControllerGetSerial(self.controller)
        except NameError:
            pass
        try:
            self.player_index = SDL_GameControllerGetPlayerIndex(self.controller)
        except NameError:
            return

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        if self.opened:
            self.opened = False
            SDL_GameControllerClose(self.controller)
        del self.app
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
