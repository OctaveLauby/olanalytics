import bisect
import numpy as np
from collections.abc import Iterable
from datetime import datetime
from functools import partial


def check_method(instance, attr, reference):
    """Return whether value return by method matches reference"""
    attr_val = getattr(instance, attr)()
    return check_value(attr_val, reference=reference)


def check_property(instance, attr, reference):
    """Return whether value of property matches reference"""
    attr_val = getattr(instance, attr)
    return check_value(attr_val, reference=reference)


def check_value(val, reference):
    """Return whether value matches reference

    Args:
        val (scalar)
        reference (scalar|list|tuple)
            scalar      check if val == reference
            list        check if check_value(val, ref) for ref in reference
            tuple       check if reference[0] <= val <= reference[1]
    """
    if isinstance(reference, list):
        for ref in reference:
            if check_value(val, ref):
                return True
        return False
    if isinstance(reference, tuple):
        return reference[0] <= val <= reference[1]
    return val == reference



class DatetimeDescription:
    """Description of a datetime"""

    def __init__(self, **attributes):
        """Create a time description

        **attributes: expected values of datetime attributes
            for instance attributes = {
                'hour': 5,          # hour is 5
                'day': (1, 15),     # month day number b/w 1 on 15
                'weekday': 5,       # week day number is 5
            }
        """
        self._attributes = attributes
        self._pipe = []
        for attr, value in attributes.items():
            if hasattr(datetime, attr) and callable(getattr(datetime, attr)):
                check_func = check_method
            elif hasattr(datetime, attr):
                check_func = check_property
            else:
                raise AttributeError(f"datetime has no attribute called f'{attr}'")
            func = partial(check_func, attr=attr, reference=value)
            func.__name__ = f"{attr}={repr(value)}"
            self._pipe.append(func)

    def match(self, dt):
        """Return whether datetime match timedescription"""
        for func in self._pipe:
            if not func(dt):
                return False
        return True

    def match_indexes(self, dts):
        """Return indexes within dts where datetimes match description"""
        return np.where(self.matches(dts))[0]

    def matches(self, dts):
        """Return array of bool where dts match description"""
        res = [self.match(dt) for dt in dts]
        if isinstance(dts, np.ndarray):
            return np.array(res)
        return res

    def __repr__(self):
        return f"{self.__class__.__name__}[{self}]"

    def __str__(self):
        return "|".join(func.__name__ for func in self._pipe)


def dtloc2pos(__object, timeline):
    """Convert a datetime location to an array of indexes within timeline

    In case object is slice, return slice at it is
    """

    if isinstance(__object, slice):
        return __object
    if isinstance(__object, datetime):
        index = bisect.bisect_left(timeline, __object)
        if timeline[index] != __object:
            res = []
        else:
            res = [index]
    elif isinstance(__object, (DatetimeDescription, dict)):
        if isinstance(__object, dict):
            __object = DatetimeDescription(**__object)
        res = __object.match_indexes(timeline)
    elif isinstance(__object, int):
        res = [__object]
    elif isinstance(__object, Iterable):
        res = []
        for item in __object:
            res = np.union1d(res, dtloc2pos(item, timeline))
    else:
        raise TypeError(f"Unknown type {type(__object)}")

    return np.array(res)
