import numpy as np


def best_values(series, nb=None, min_count=None):
    """Return unique values in series ordered by most to less occurrences"""
    occurrences = series.value_counts()
    if min_count:
        occurrences = occurrences[occurrences > min_count]
    nb = len(occurrences) if nb is None else nb
    return list(occurrences.index[:nb])


def required_values(series, target_ratio):
    """Return unique values required to cover ratio of usage in series

    Args:
        series (pandas.Series): list values
        target_ratio (float): ratio of total usage to reach
            nans are not counted as 'usage'
            for instance in [1, numpy.nan, 2], 1 represents 50% of usage
    """
    item_occurrences = series.value_counts()
    total_occurrences = sum(item_occurrences)
    target = target_ratio * total_occurrences
    items, usage = [], 0
    for item, occurrences in item_occurrences.iteritems():
        usage += occurrences
        items.append(item)
        if usage > target:
            break
    prc = 100 * len(items) / len(item_occurrences)
    t_prc = 100 * (usage / total_occurrences)
    print(
        f". {len(items)} / {len(item_occurrences)} ({prc:0.2f}%)"
        f" items required to reach {t_prc:0.2f}% of usage"
    )
    return items


def required_weights(weights, target_ratio, as_ratio=False):
    """Return weights required to reach target_ratio"""
    res = weights[required_weights_i(weights, target_ratio, as_ratio=as_ratio)]
    prc = 100 * len(res) / len(weights)
    if as_ratio:
        t_prc = 100 * sum(res)
    else:
        t_prc = 100 * (sum(res) /sum(weights))
    print(
        f". {len(res)} / {len(weights)} ({prc:0.2f}%)"
        f" {'ratio' if as_ratio else 'weight'}s required to reach {t_prc:0.2f}%"
        + ("" if as_ratio else " of total weight")
    )
    return res


def required_weights_i(weights, target_ratio, as_ratio=False):
    """Return indexes of weights required to reach target_ratio"""
    assert (weights >= 0).all()
    if as_ratio:
        ratios = weights
    else:
        ratios = weights / sum(weights)
    sindexes = np.argsort(-ratios)
    rindexes = []
    total_r = 0
    for i in sindexes:
        if total_r >= target_ratio:
            break
        total_r += ratios[i]
        rindexes.append(i)

    return np.array(rindexes)
