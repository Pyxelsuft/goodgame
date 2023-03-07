def njit(nopython: bool = False, fastmath: bool = False, cache: bool = False) -> any:  # noqa
    def wrapper(func: any) -> any:
        return func
    return wrapper
