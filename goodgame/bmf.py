from sdl2 import *


class BMFont:
    def __init__(self, data: str) -> None:
        self.destroyed = True
        self.raw_data = data
        self.data = self.parse()
        self.destroyed = False
        # TODO: finish

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
                attr_value = self.get_attr(attr_spl[1])
                data[attr_name] = attr_value
            result.append((name, data))
        return result

    def get_attr(self, attr_val: str) -> any:
        if attr_val.replace('-', '').isdigit():
            return int(attr_val)
        if attr_val.startswith('"') and attr_val.endswith('"'):
            return attr_val[1:-1].replace('\\"', '"')
        if ',' in attr_val:
            return [self.get_attr(_x) for _x in attr_val.split(',')]
        return attr_val

    def destroy(self) -> bool:
        if self.destroyed:
            return True
        self.destroyed = True
        return False

    def __del__(self) -> None:
        self.destroy()
