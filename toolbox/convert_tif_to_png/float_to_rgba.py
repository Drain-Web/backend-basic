import numpy as np


def float_to_rgb(data: np.array) -> tuple:
    """
    Blue gradient. Assumes values from 0 to 1.
    """

    filter = (data > 0)
    r_channel = filter * (data * 0.5)
    g_channel = filter * (data * 1.0)
    b_channel = filter * (data * 2.5)

    return r_channel, g_channel, b_channel


def float_to_alpha(data: np.array) -> np.array:
    """
    Everything under -1.5 is total transparent, total opaque otherwise.
    """

    return np.uint((data > -1.5)*255)
