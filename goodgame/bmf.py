from .texture import Texture
from sdl2 import *


class BMChar:
    def __init__(self, renderer: any, data: dict, page: Texture) -> None:
        self.destroyed = True
        self.id = data['id']
        self.chr = chr(self.id)
        self.pos = (data['x'], data['y'])
        self.size = (data['width'], data['height'])
        self.offset = (data['xoffset'], data['yoffset'])
        self.x_adv = data['xadvance']
        self.page = data['page']
        self.channel = data['chnl']
        self.letter = data['letter']
        if not self.size[0] or not self.size[1]:
            self.texture = None
            return
        self.texture = renderer.crop_texture(page, (
            self.pos[0],
            self.pos[1],
            self.size[0],
            self.size[1]
        ))
        self.texture.set_blend_mode('blend')
        self.destroyed = False

    def __add__(self, other: any) -> int:
        return self.x_adv + other

    def __radd__(self, other: any) -> any:
        if other == 0:
            return self
        return self.x_adv + other

    def __int__(self) -> int:
        return self.x_adv

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.texture.destroy()
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()


class BMFont:
    def __init__(self, renderer: any, data: str, files: dict = None) -> None:
        self.destroyed = True
        self.renderer = renderer
        self.format = self.renderer.pixel_format_from_str('rgba8888')
        self.files = files or {}
        self.raw_data = data
        self.info = {}
        self.common = {}
        self.pages = {}
        self.num_chars = 0
        self.num_kernings = 0
        self.chars = {}
        self.data = self.parse()
        self.parse_data()
        self.destroyed = False
        # TODO:
        #  render lines (including split by width, wrap align, etc)

    def render(self, line: str) -> Texture:
        cur_x = 0
        chars = [self.chars.get(char_str) or self.chars['?'] for char_str in line]
        tex: Texture = self.renderer.create_texture(
            (sum(chars) + chars[-1].size[0] - chars[-1].x_adv, self.common['lineHeight']),
            self.format
        )
        tex.set_blend_mode('blend')
        self.renderer.set_target(tex)
        self.renderer.clear((0, 0, 0, 0))
        for char in chars:
            char.texture and self.renderer.blit(char.texture, dst_rect=(cur_x + char.offset[0], char.offset[1]))
            cur_x += char.x_adv
        self.renderer.set_target(None)
        return tex

    def parse_data(self) -> None:
        for data in self.data:
            if data[0] == 'info':
                self.info = data[1]
            elif data[0] == 'common':
                self.common = data[1]
            elif data[0] == 'page':
                self.pages[data[1]['id']]: Texture = self.files.get(data[1]['file'])
            elif data[0] == 'chars':
                self.num_chars = data[1]['count']
            elif data[0] == 'char':
                bm_char = BMChar(self.renderer, data[1], self.pages[data[1]['page']])
                if bm_char.letter == 'space':
                    self.chars[' '] = bm_char
                    if not self.chars.get('\n'):
                        data[1]['letter'] = '\n'
                        self.chars['\n'] = BMChar(self.renderer, data[1], self.pages[data[1]['page']])
                else:
                    self.chars[bm_char.letter] = bm_char
            elif data[0] == 'kernings':
                self.num_kernings = data[1]['count']

    def parse(self) -> list:
        data_spl = self.raw_data.split('\n')
        result = []
        for line in data_spl:
            if not line:
                continue
            line_spl = line.split(' ')
            name = line_spl[0]
            data = {}
            for attr_str in line_spl[1:]:
                if not attr_str:
                    continue
                attr_spl = attr_str.split('=')
                attr_name = attr_spl[0]
                attr_value = self.get_attribute(attr_spl[1])
                data[attr_name] = attr_value
            result.append((name, data))
        return result

    def get_attribute(self, attr_val: str) -> any:
        if attr_val.replace('-', '').isdigit():
            return int(attr_val)
        if attr_val.startswith('"') and attr_val.endswith('"'):
            return attr_val[1:-1].replace('\\"', '"')
        if ',' in attr_val:
            return [self.get_attribute(_x) for _x in attr_val.split(',')]
        return attr_val

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.pages.clear()
        self.files.clear()
        del self.renderer
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
