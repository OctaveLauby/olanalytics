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