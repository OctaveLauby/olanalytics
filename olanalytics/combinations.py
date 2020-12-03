import itertools
import numpy as np
import random as rd


def combinations_ij(n):
    """Return (i, j) combinations with 0 <= i < j < n"""
    return itertools.combinations(range(n), 2)


def combinations_nb(n):
    """Return number of (i, j) combinations with 0 <= i < j < n"""
    return (n * (n-1)) // 2


def combinations_ij_sample(n, number):
    """Return random sample of (i, j) combinations with 0 <= i < j < n"""
    max_number = combinations_nb(n)
    number = min(number, max_number)
    sample_indexes = sorted(rd.sample(range(max_number), number))
    for cindex in sample_indexes:
        yield S_inv(cindex, n)


def S_inv(cindex, n):
    """Return combination i, j given its index in combinations_ij iterator"""

    # Solving S(i, i+1, n) = cindex
    a = (-1/2)
    b = (n - 1/2)
    c = -cindex
    delta = b**2 - 4*a*c
    ix = (b-np.sqrt(delta)) / (-2*a)

    # Gathering i, j
    i = int(ix)
    j = cindex - S(i, i+1, n) + i + 1
    return i, j



def S(i, j, n):
    """Return index of combination i, j in combinations_ij iterator"""
    res = (-1/2)*i**2 + (n - 3/2)*i + (j - 1)
    return int(res)
