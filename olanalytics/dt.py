from datetime import datetime
from functools import partial
import numpy as np


def check_method(dt, attr, value):
    attr_val = getattr(dt, attr)()
    if isinstance(value, tuple):
        return value[0] <= attr_val <= value[1]
    return attr_val == value


def check_property(dt, attr, value):
    attr_val = getattr(dt, attr)
    if isinstance(value, tuple):
        return value[0] <= attr_val <= value[1]
    return attr_val == value


class DatetimeDescription:
    def __init__(self, **attributes):
        """Create a time description"""
        self._attributes = attributes
        self._pipe = []
        for attr, value in attributes.items():
            if hasattr(datetime, attr) and callable(getattr(datetime, attr)):
                check_func = check_method
            elif hasattr(datetime, attr):
                check_func = check_property
            else:
                raise AttributeError(f"datetime has no attribute called f'{attr}'")
            func = partial(check_func, attr=attr, value=value)
            func.__name__ = f"{attr}={repr(value)}"
            self._pipe.append(func)

    def match(self, dt):
        """Return whether datetime match timedescription"""
        for func in self._pipe:
            if not func(dt):
                return False
        return True

    def match_indexes(self, dts):
        return np.where(self.matches(dts))[0]

    def matches(self, dts):
        res = [self.match(dt) for dt in dts]
        if isinstance(dts, np.ndarray):
            return np.array(res)
        return res

    def __repr__(self):
        return f"{self.__class__.__name__}[{self}]"

    def __str__(self):
        return "|".join(func.__name__ for func in self._pipe)
