import numpy as np

from olanalytics import detection


def test_group_consecutives():
    np.testing.assert_equal(
        detection.group_consecutives([0, 1, 3, 4, 5, 7, 9, 10]),
        [[0, 1], [3, 4, 5], [7], [9, 10]]
    )
    np.testing.assert_equal(
        detection.group_consecutives([0, 1, 3, 4, 5, 7, 9, 10], 2),
        [[0], [1, 3], [4], [5, 7, 9], [10]]
    )
    np.testing.assert_equal(
        detection.group_consecutives([.5, 1, 2, 3.5, 4.5, 5]),
        [[.5], [1, 2], [3.5, 4.5], [5]]
    )


def test_linearize():
    np.testing.assert_equal(
        detection.linearize([0, 5, 6, 13, 16]),
        [0, 4, 8, 12, 16],
    )
    np.testing.assert_equal(
        detection.linearize([0, 5, 6, 13, 16], index=2),
        [0, 3, 6, 11, 16],
    )
    np.testing.assert_equal(
        detection.linearize([0, 5, 6, 13, 16, 21, 2, 0]),
        [0] * 8,
    )
    np.testing.assert_equal(
        detection.linearize([0, 5, 6, 13, 16, 21, 2], index=4),
        [0, 4, 8, 12, 16, 9, 2],
    )


def test_detect_elbow():

    X = np.array([0, 1, 2, 3, 4, 6, 8, 10])
    assert detection.detect_elbow(X) == 4
    assert detection.detect_elbow(X, mthd="singleline") == 4
    assert detection.detect_elbow(X, mthd="doubleline") == 4

    X = np.array([0.35, 0.36, 0.37, 0.40, 0.42, 0.49, 0.53, 0.65, 0.95, 1.35])
    assert detection.detect_elbow(X) == 6
    assert detection.detect_elbow(X, mthd="singleline") == 6
    assert detection.detect_elbow(X, mthd="doubleline") == 7


def test_detect_iso():
    a = np.array([10000, 2950, 3000, 2900, 2200, 3000, 2800, 2850, 2200, 1500])
    np.testing.assert_equal(
        detection.detect_iso(a),
        [0, 4, 9]
    )
    np.testing.assert_equal(
        detection.detect_iso(a, delta_r=0.099, lvlref=2000),
        [0, 4, 5, 9]
    )

    a = np.array([3025, 3000, 2900, 3100, 2200, 3000, 2850, 2200, 2000])
    np.testing.assert_equal(detection.detect_iso(a), [4])

    np.testing.assert_equal(detection.detect_iso(np.array([1, 10000])), [])
    np.testing.assert_equal(detection.detect_iso(np.array([11, 12, 13])), [])
    np.testing.assert_equal(
        detection.detect_iso(np.array([1, 10, 1])),
        [0, 1, 2]
    )


def test_detect_leap():

    X = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    Y = np.array([6, 6, 4, 8, 8, 1, 1, 6])

    assert detection.detect_leap(None, Y, thld=3) == [3, 7]
    assert detection.detect_leap(None, Y, thld=4) == [3, 7]
    assert detection.detect_leap(None, Y, thld=3, lvl_thld=7) == [3]
    assert detection.detect_leap(X, Y, thld=3, onspan=1) == [3, 7]
    assert detection.detect_leap(X, Y, thld=4, onspan=1) == [7]
    assert detection.detect_leap(X, Y, thld=3, onspan=1, wfading=0.5) == [3, 7]

    assert detection.detect_leap(None, Y, thld=-3) == [5]
    assert detection.detect_leap(None, Y, thld=-3, lvl_thld=0) == []
    assert detection.detect_leap(None, Y, thld=-3, lvl_thld=1) == [5]
    assert detection.detect_leap(None, Y, thld=-3, lvl_thld=2) == [5]
    assert detection.detect_leap(X, Y, thld=-3, onspan=1) == [5]
    assert detection.detect_leap(X, Y, thld=-3, onspan=2) == [5]


def test_reg_bounds():
    values = np.array([0, 1, 2, 3, 4, 1, 0, 5, 6])
    assert detection.reg_bounds(values, bot_thld=2, top_thld=4) == [
        2, 5, 7
    ]


def test_stepreg_bounds():
    ticks = np.array([0, 1, 2, 4, 6, 8, 11, 12, 16, 20, 22])
    assert detection.stepreg_bounds(ticks, bot_thld=2, top_thld=3) == [
        2, 6, 7, 9
    ]
    assert detection.stepreg_bounds(ticks, top_thld=1) == [2, 6, 7]
    assert detection.stepreg_bounds(ticks, top_thld=10) == []
