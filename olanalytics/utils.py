import functools
import numpy as np
import pandas as pd


def handle_na(func):
    """Decorator for scalar function so it returns nan when nan is input"""

    @functools.wraps(func)
    def func_wrapper(arg, *args, **kwargs):
        if pd.isna(arg):
            return arg
        return func(arg, *args, **kwargs)

    func_wrapper.__doc__ = func.__doc__ if func.__doc__ else ""
    func_wrapper.__doc__ += "\n@about: return numpy.nan if arg is nan\n"

    return func_wrapper


def notna(obj):
    """Detect none missing values for an array-like or scalar object."""
    return np.logical_not(pd.isna(obj))
