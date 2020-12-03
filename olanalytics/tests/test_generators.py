import numpy as np
from datetime import datetime, timedelta

from olanalytics.dt import DatetimeDescription
from olanalytics.generators import timeseries, CustomTimedCurve


def test_dt_generation():

    X = timeseries(
        start=datetime(2020, 1, 1),
        end=datetime(2020, 1, 2),
        step=timedelta(hours=1),
    )
    np.random.seed(seed=30)
    curve = CustomTimedCurve(X)
    curve.add_noise(0, 1, loc=DatetimeDescription(hour=[(0, 8), (18, 24)]))
    curve.add_noise(0, 3, loc=DatetimeDescription(hour=[(8, 18)]))
    curve.add_gaussian(8, center=DatetimeDescription(hour=12), stdev=1)
    curve.set_zero(loc=DatetimeDescription(hour=[2, 14]))
    np.testing.assert_almost_equal(
        curve.Y,
        [
            0.644143536068335,
            0.38074848963511654,
            0.0,
            0.16365072610275336,
            0.96260781367442,
            0.34666184056294447,
            0.9917511141334456,
            0.23508770883102223,
            0.8574881179026603,
            0.6761857426160136,
            4.065263318784986,
            5.557786770552034,
            8.716959115827953,
            6.739544770182674,
            0.0,
            2.15390512150755,
            0.09607594627610168,
            2.7075713429709816,
            1.2659962072021014,
            0.13623432220222573,
            0.5441362876382811,
            0.5181763468258455,
            0.7668551062985054,
            0.9338501433185797,
        ]
    )
