import matplotlib.pyplot as plt
import pytest

import olanalytics.plotting.setters as lib


def test_set_size():
    lib.set_size()
    assert plt.rcParams['figure.figsize'] == [17, 4]

    lib.set_size(10, 5)
    assert plt.rcParams['figure.figsize'] == [10, 5]


def test_set_style():

    with pytest.raises(ValueError):
        lib.set_style('unknown')

    assert plt.rcParams['patch.facecolor'] == "C0"
    lib.set_style()
    assert plt.rcParams['patch.facecolor'] == "#4C72B0"

