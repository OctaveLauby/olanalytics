"""Functions to detect irregularities"""
import numpy as np


# --------------------------------------------------------------------------- #
# Utils


def linearize(a, index=-1):
    """Linearize vector in 2 linear segments

    Assumption: a is based on regular step

    Args:
        a (np.ndarray)
        index (int): index where to split linearization
            if index out of bounds, return one segment

    Return:
        (np.ndarray)
    """
    if index <= 0 or index >= (len(a) - 1):
        return ((a[-1] - a[0]) / (len(a)-1)) * np.arange(0, len(a)) + a[0]

    y = a[index]
    fst_seg = ((y - a[0]) / index) * np.arange(index+1) + a[0]
    rindex = len(a) - index - 1
    lst_seg = ((a[-1] - y) / rindex) * np.arange(rindex+1) + y
    return np.concatenate([fst_seg, lst_seg[1:]])


def group_consecutives(a, step=1):
    """Group step-consecutive elements in a list of arrays

    Example:
        >> group_consecutives([1, 2, 4, 5, 6, 9], step=1)
        [[1, 2], [4, 5, 6], [9]]
    """
    if len(a) == 0:
        return []
    return np.split(a, np.where(np.diff(a) != step)[0] + 1)


# --------------------------------------------------------------------------- #
# Algorithms


# ----------------------------------- #
# Regularity

def reg_bounds(X, bot_thld=0, top_thld=np.inf):
    """Detect regularity and return boundaries for consistent splitting

    Args:
        X (np.ndarray)  : array to work with
        bot_thld (float): bot threshold for x
        top_thld (float): top threshold for x

    Returns:
        (int-list)
            indexes where to split X so each span has x-values with either
                with bot_thld <= x <= top_thld
                with x < bot_thld
                with top_thld < x

    Example:
        >> values = np.array([0, 1, 2, 3, 4, 1, 0, 5, 6])
        >> detection.reg_bounds(values, bot_thld=2, top_thld=4)
        [2, 5, 7]
    """
    if bot_thld > top_thld:
        raise ValueError("bot_thld must be smaller or equal to top_thld")

    if len(X) == 0:
        return []

    indexes_forsplit = set()

    # Small steps
    if bot_thld > 0:
        indexes = np.where(X < bot_thld)[0]
        igroups = group_consecutives(indexes)
        for igroup in igroups:
            indexes_forsplit.add(igroup[0])
            indexes_forsplit.add(igroup[-1] + 1)

    # Wide steps
    if top_thld != np.inf:
        indexes = np.where(X > top_thld)[0]
        igroups = group_consecutives(indexes)
        for igroup in igroups:
            indexes_forsplit.add(igroup[0])
            indexes_forsplit.add(igroup[-1] + 1)

    try:
        indexes_forsplit.remove(0)
    except KeyError:
        pass
    try:
        indexes_forsplit.remove(len(X))
    except KeyError:
        pass
    return sorted(indexes_forsplit)


def stepreg_bounds(X, *args, **kwargs):
    """Detect step regularity and return boundaries for consistent splitting

    Args:
        X (np.ndarray)  : array to work with
        bot_thld (float): bot threshold for step
        top_thld (float): top threshold for step

    Returns:
        (int-list)
            indexes where to split X so each span has x-diffs with either:
                with bot_thld <= x_i+1 - x_i <= top_thld
                with x_i+1 - x_i < bot_thld
                with top_thld < x_i+1 - x_i
    """
    if len(X) <= 1:
        return []
    steps = np.diff(X)  # step_i refers to X[i], X[i+1]
    return reg_bounds(steps, *args, **kwargs)


# ----------------------------------- #
# Elbow

def detect_elbow(Y, mthd='singleline'):
    """Return index where elbow occurs

    Args:
        Y (np.ndarray)
        mthd (str): method to find elbow
            singleline> find farthest pt from fst-pt to lst-pt line
            doubleline> find pt where dist(fst-pt to pt to lst-pt, Y) is min

    Return:
        index (int)
    """
    if mthd == 'singleline':
        line = linearize(Y)
        return np.argmax(np.sqrt((Y-line)**2))
    elif mthd == 'doubleline':
        bst_index, bst_dist = None, np.inf
        for index, y in enumerate(Y[1:-1], 1):
            curve = linearize(Y, index)
            dist = np.linalg.norm(Y - curve)
            if dist <= bst_dist:
                bst_index, bst_dist = index, dist
        return bst_index
    else:
        raise ValueError("Unknown detection method '%s' % method")


# ----------------------------------- #
# Leap

def detect_iso(Y, delta_r=0.1, lvlref=None):
    """Return indexes of isolated points

    About:
        First Y is shifted so each value is >=0
        Yj is isolated if [i=j-1 and k=j+1]:
            not (b/w Yi and Yk)
            and min(|Yi - Yj / lvlref|, |Yk - Yj / lvlref|) > delta_r
        Borders can be isolated if ratio with closest Y is > delta_r

        Won't work properly iY has negative values

    Args:
        Y (float np.ndarray): list of values
        delta_r (float): max factor b/w lvlref and neighbors
        lvlref (float or callable): lvlref or func to compute lvlref from Y
            default is 9th percentile

    Return:
        (int-np.ndarray) indexes of isolated points
    """
    if len(Y) <= 2:
        return np.array([])

    lvlref = (
        lvlref if isinstance(lvlref, (float, int))
        else (
            lvlref(Y) if lvlref
            else np.percentile(Y, 90, interpolation="lower")
        )
    )
    if lvlref <= 0:
        raise ValueError("lvlref=%s <= 0" % lvlref)

    # Compute isolated points in center of Y
    dY = np.diff(Y)
    dY_l = -dY[:-1]
    dY_r = dY[1:]

    inbetween = dY_l * dY_r < 0
    delta = np.min([np.abs(dY_l) / lvlref, np.abs(dY_r) / lvlref], axis=0)

    # Add borders
    inbetween = np.concatenate([[False], inbetween, [False]])
    delta = np.concatenate(
        [[np.abs(dY[0]) / lvlref], delta, [np.abs(dY[-1]) / lvlref]]
    )

    return np.where((1 - inbetween) * (delta > delta_r))[0]


def detect_leap(X, Y, thld, lvl_thld=None, onspan=None, wfading=None):
    """Return indexes where leap is detected on Y

    Args:
        X (n-numpy.ndarray)
        Y (n-numpy.ndarray)
        thld (float)        : min diff b/w consecutive values to consider leap
            if thld is neg, thld considered as max diff b/w consec. values
        lvl_thld (float)    : min new value to consider leap
            if thld is neg, lvl_thld considered as max new value
        onspan (float)      : given a detected leap at x,
            compute prev_y on ticks b/w prev_x - onspan & prev_x
            compute next_y on ticks b/w x & x + onspan
        wfading (float): when computing prev_y or next_y, apply weight to
            each selected y_val [weight = 1 - wfading * |x-x_ref| / onspan]

    Return:
        indexes (list) where y_i - y_i-1 >= deltaU_thld and y_i >= U_thld
    """
    indexes = []

    def flag(py, ny):
        res = ((ny - py) >= thld) if thld >= 0 else ((ny - py) <= thld)
        if lvl_thld is not None:
            res *= (ny >= lvl_thld) if thld >= 0 else (ny <= lvl_thld)
        return res
    indexes = list(np.argwhere(flag(Y[:-1], Y[1:])).flatten() + 1)

    if not onspan:
        return indexes

    findexes = []
    wfading = 0 if wfading is None else wfading
    if not 0 <= wfading <= 1:
        raise ValueError("wfading must be b/w 0 and 1")

    def weight(x, ref):
        return 1 - wfading * np.abs(x - ref) / onspan

    for i in indexes:

        ref_x = X[i-1]
        j = i - 1
        sl = []
        while j >= 0 and X[j] >= ref_x - onspan:
            sl.insert(0, j)
            j -= 1
        prevX, prevY = X[sl], Y[sl]
        prevW = weight(prevX, ref_x)

        ref_x = X[i]
        j = i
        sl = []
        while j < len(Y) and X[j] <= ref_x + onspan:
            sl.append(j)
            j += 1
        nextX, nextY = X[sl], Y[sl]
        nextW = weight(nextX, ref_x)

        prev_y = sum(prevY * prevW) / sum(prevW)
        next_y = sum(nextY * nextW) / sum(nextW)

        if flag(prev_y, next_y):
            findexes.append(i)

    return findexes
