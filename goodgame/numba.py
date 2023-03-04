def jit(nopython: bool = False, fastmath: bool = False) -> any:  # noqa
    def wrapper(func: any) -> any:
        return func
    return wrapper
