def njit(
    nopython: bool = False, fastmath: bool = False, cache: bool = False, parallel: bool = False  # noqa
) -> any:
    def wrapper(func: any) -> any:
        return func
    return wrapper


prange = range  # noqa
