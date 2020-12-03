import numpy as np
import pytest
from datetime import datetime

import olanalytics.dt as lib


def test_DatetimeDescription():
    dd = lib.DatetimeDescription(weekday=0)
    assert dd.match(datetime(2020, 1, 6))
    assert not dd.match(datetime(2020, 1, 7))

    dd = lib.DatetimeDescription(hour=7)
    assert dd.match(datetime(2020, 1, 6, 7))
    assert not dd.match(datetime(2020, 1, 6, 8))
    assert dd.match(datetime(2020, 1, 7, 7))
    assert not dd.match(datetime(2020, 1, 7, 8))

    dd = lib.DatetimeDescription(weekday=0, hour=7)
    assert dd.match(datetime(2020, 1, 6, 7))
    assert not dd.match(datetime(2020, 1, 6, 8))
    assert not dd.match(datetime(2020, 1, 7, 7))
    assert not dd.match(datetime(2020, 1, 7, 8))

    dd = lib.DatetimeDescription(hour=(6, 8))
    assert not dd.match(datetime(2020, 1, 1, 5))
    assert dd.match(datetime(2020, 1, 1, 6))
    assert dd.match(datetime(2020, 1, 1, 7))
    assert dd.match(datetime(2020, 1, 1, 8))
    assert not dd.match(datetime(2020, 1, 1, 9))

    dd = lib.DatetimeDescription(hour=[6, 8])
    assert not dd.match(datetime(2020, 1, 1, 5))
    assert dd.match(datetime(2020, 1, 1, 6))
    assert not dd.match(datetime(2020, 1, 1, 7))
    assert dd.match(datetime(2020, 1, 1, 8))
    assert not dd.match(datetime(2020, 1, 1, 9))


def test_dtloc2pos():

    def assert_eq(res, expected):
        assert isinstance(res, np.ndarray)
        np.testing.assert_equal(res, expected)

    timeline = [
        datetime(2020, 1, 6, 8),
        datetime(2020, 1, 6, 9),
        datetime(2020, 1, 7, 7),
        datetime(2020, 1, 7, 8),
        datetime(2020, 1, 7, 9),
    ]

    # dict, DatetimeDescription
    params = {'hour': 8}
    expected = [0, 3]
    assert_eq(lib.dtloc2pos(params, timeline), expected)
    dd = lib.DatetimeDescription(**params)
    assert_eq(lib.dtloc2pos(dd, timeline), expected)

    # None/nan
    with pytest.raises(TypeError):
        lib.dtloc2pos(None, timeline)
    with pytest.raises(TypeError):
        lib.dtloc2pos(np.nan, timeline)

    # Slice
    assert lib.dtloc2pos(slice(1, 2), timeline) == slice(1, 2)

    # Datetime
    assert_eq(
        lib.dtloc2pos(datetime(2020, 1, 6, 9), timeline),
        [1],
    )
    assert_eq(
        lib.dtloc2pos(datetime(2020, 1, 6, 9, 30), timeline),
        [],
    )

    # Iterable
    assert_eq(
        lib.dtloc2pos([{'hour': 7}, {'hour': 9}], timeline),
        [1, 2, 4],
    )
