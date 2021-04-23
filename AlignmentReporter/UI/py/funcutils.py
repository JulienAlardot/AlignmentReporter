import time
from typing import List

import numpy as np


def compute_time(t):
    """
    Function that convert a given time value into a string

    :param t: Time in second
    :type t: float
    :return: Time string
    :rtype: str
    """
    force = False
    p = "Process took: "
    if t >= 60 ** 2:
        force = True
        h = int(t / 60 ** 2)
        if h > 1:
            p += "{:2} hours, ".format(h)
        else:
            p += "{:2} hour, ".format(h)

        t %= 60 ** 2

    if t >= 60 or force:
        force = True
        m = int(t / 60)
        if m > 1:
            p += "{:2} minutes, ".format(m)
        else:
            p += "{:2} minute, ".format(m)

        t %= 60

    if t > 1:
        p += "{} seconds".format(round(t, 2))
    else:
        p += "{} second".format(round(t, 2))
    return p


def timeit(func):
    """
    Decorator function computing the excecution time of a function

    :param func: Function to decorate
    :type func: function
    :return: wrapped func
    :rtype: function
    """

    def inner(*args, **kwargs):
        inner.__doc__ = timeit.__doc__
        start = time.time()
        result = func(*args, **kwargs)
        print(func.__name__ + " " + str(round(time.time() - start, 4)))
        return result

    return inner


def alignment_to_position(entries, first_entry_weight):
    """
    Transform a given list of string alignment entries into positional entries. Apply a weight modifier to the first
    entry of the list

    :param entries: 1D-array of string entries like ('LG', 'NG', 'CG', ...)
    :param first_entry_weight: Weight of the first entry of the "entries" parameter
    :type entries: tuple or list or np.ndarray
    :return: List of positional values
    :rtype: tuple[tuple[float, float]]
    """
    values: List[List[float, float]] = []
    value: List[str] = list()
    for i, old_value in enumerate(entries):
        x = []
        y = []
        if len(old_value) == 2:
            value = [old_value[0], old_value[1]]  # jit forced manual list(str) conversion
            if value[0] == "N":
                value[0] = "T"
        elif len(old_value) == 1:
            value = [old_value[0]]

        for v in value:
            if v == "L":
                x.append(-1.)
            elif v == "T":
                x.append(0.)
            elif v == "C":
                x.append(1.)
            elif v in ('G', 'B'):
                y.append(1.)
            elif v == "N":
                y.append(0.)
            elif v in ("E", 'M'):
                y.append(-1.)
        if len(x) > len(y):
            for j in range(len(x) - len(y)):
                y.append(np.nan)
        elif len(y) > len(x):
            for j in range(len(y) - len(x)):
                x.append(np.nan)
        if i == 0:
            for j in range(0, max(0, first_entry_weight - 1)):
                values += list(zip(x, y))
        values += tuple(list(zip(x, y)))
    return tuple(values)
