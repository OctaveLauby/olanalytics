import bisect
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

from olanalytics.dt import DatetimeDescription



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

    def add_noise(self, low, high):
        """Add uniform noise to Y"""
        self.Y += np.random.uniform(
            low=low,
            high=high,
            size=len(self),
        )

    def add_gaussian(self, high, center, stdev):
        """Add gaussian to Y

        center is based on numerical X
        """
        assert stdev > 0
        print(stdev)
        self.Y += high * np.exp(-0.5 * (self.Xnum-center)**2 / stdev**2)

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
        """timed X vector (datetimes)"""
        return self._T

    @property
    def step(self):
        """Step between to steps"""
        return self._step

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
        if isinstance(center, datetime):
            index = bisect.bisect_left(self.X, center)
            if self.X[index] != center:
                raise NotImplementedError("center not in time line")
            indexes = [index]
        elif isinstance(center, (DatetimeDescription, dict)):
            if isinstance(center, dict):
                center = DatetimeDescription(**center)
            indexes = center.match_indexes(self.X)
        elif isinstance(center, (float, int)):
            indexes = [center]
        else:
            raise TypeError(f"Unknown type center {type(center)}")

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
