import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

from olanalytics.dt import dtloc2pos



def timeseries(start, end, step):
    X = []
    x = start
    while x < end:
        X.append(x)
        x += step
    return np.array(X)


class CustomCurve:

    def __init__(self, X):
        """Initiate a new curve (Y=zeros)

        assume x has regular step
        """
        self._Xnum = X
        self.Y = np.zeros(len(X))

    @property
    def X(self):
        """X vector"""
        return self._Xnum

    @property
    def Xnum(self):
        """Numerical X vector"""
        return self._Xnum

    def add_noise(self, low, high, loc=None):
        """Add uniform noise to Y"""
        loc = slice(0, len(self.Y)) if loc is None else loc
        self.Y[loc] += np.random.uniform(
            low=low,
            high=high,
            size=len(self.Y[loc]),
        )

    def add_gaussian(self, high, center, stdev):
        """Add gaussian to Y

        center is based on numerical X
        """
        if callable(high):
            high = high()
        assert stdev > 0
        self.Y += high * np.exp(-0.5 * (self.Xnum-center)**2 / stdev**2)

    def set_zero(self, loc=None):
        """Set value to zero"""
        self.Y[loc] -= self.Y[loc]

    def iterpoints(self):
        return zip(self.X, self.Y)

    def plot(self, *args, **kwargs):
        plt.plot(self.X, self.Y, *args, **kwargs)

    def __len__(self):
        return len(self.X)


class CustomTimedCurve(CustomCurve):

    def __init__(self, X):
        """Initiate timed curve (X are datetimes, Y set to zeros)

        assumes X has regular step and is sorted
        """
        self._T = X
        self._step = X[1] - X[0]
        X = np.array(range(len(X)))
        super().__init__(X)

    @property
    def X(self):
        """timeline vector (datetimes)"""
        return self._T

    @property
    def step(self):
        """Step between to steps"""
        return self._step

    def add_noise(self, low, high, loc=None):
        """Add uniform noise to Y"""
        loc = dtloc2pos(loc, self.X)
        return super().add_noise(low, high, loc=loc)

    def add_gaussian(self, high, center, stdev):
        """Add gaussian to Y

        Args:
            high (float)    : high of peak
            center (datetime|dict|float|int): center of gaussian
                datetime    > datetime to center gaussian on
                dict        > description of datetimes to center on
                float|int   > numerical x to center on
            stdev (timedelta|int|float): standard deviation of gaussian
                timedelta   > standard deviation on timed X
                float|int   > standard deviation on numerical X
        """
        indexes = dtloc2pos(center, self.X)

        if isinstance(stdev, timedelta):
            stdev = stdev.total_seconds() / self.step.total_seconds()
        elif not isinstance(stdev, (float, int)):
            raise TypeError(f"Unknown type center {type(center)}")

        for index in indexes:
            super().add_gaussian(
                high=high,
                center=index,
                stdev=stdev,
            )
    def set_zero(self, loc=None):
        """Set value to zero"""
        loc = dtloc2pos(loc, self.X)
        return super().set_zero(loc=loc)
