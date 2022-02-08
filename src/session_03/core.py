# No shebang line. This file is meant to be imported
"""
Core functions for the Curve Filterer tool.
"""

# standard imports
import math
import logging
import json
import os

# third-party imports
import numpy
import scipy
import scipy.ndimage

# internal imports


# logger
_log = logging.getLogger(__name__)
_log_handler = logging.StreamHandler()
_log_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
_log.addHandler(_log_handler)
_log.setLevel("INFO")

# constants


def read_curve_file(filepath):
    """Read a JSON file containing curve Y values.

    :param filepath: Path to the JSON file.
    :type filepath: str
    :raises IOError: The following path doesn't exists or doesn't have read permission
    :return: List of floats
    :rtype:list
    """

    if not os.path.exists(filepath) or not os.access(filepath, os.R_OK):
        raise IOError(
            f"The following path doesn't exists or doesn't have read permission: {filepath}"
        )

    with open(filepath, "r") as f:
        return json.load(f)


def save_curve_file(filepath, y_values):
    """Save the given curve Y values to a JSON file.

    :param filepath: Path to save the file to.
    :type filepath: str
    :param y_values: List of floats that correspond to the curve Y values.
    :type y_values: list

    :note: We do not perform any sort of check for an existing file. For a real use case you
           will want the end-user to confirm if they want to remove existing data.
    """
    print(filepath)
    with open(filepath, "w") as f:
        json.dump(y_values, f)


def smooth_values(
    values, strength=0.2, smooth_type="Savitzky-Golay", preserve_edges=False
):
    """Smooth the given values with the select algorithm.

    :param values: List of float values to smooth.
    :type values: list
    :param strength: Intensity of the smoothing, defaults to 0.2
    :type strength: float, optional
    :param smooth_type: Type of algorithm to use ("Savitzky-Golay", "Gaussian", "Moving Average", "Mean Average"), defaults to "Savitzky-Golay"
    :type smooth_type: str, optional
    :param preserve_edges: If True, keep teh first and alst values as is and blend the second and second to last smoothed value, defaults to False
    :type preserve_edges: bool, optional
    :return: Smooth values.
    :rtype: list
    """

    if smooth_type == "Savitzky-Golay":
        if strength < 0.1:
            strength = 0.1
        win_size = int(strength * 10) * 2
        filtered_values = savitzky_golay(
            values, win_size=win_size, order=2, derivative=0
        )
    elif smooth_type == "Gaussian":
        if strength < 0.1:
            strength = 0.1
        win_size = int(strength * 5)
        filtered_values = gaussian(values, win_size)
    elif smooth_type == "Moving Average":
        if strength < 0.1:
            strength = 0.1
        win_size = int(strength * 10) * 2
        filtered_values = moving_average(values, win_size)
    else:
        filtered_values = mean_average(values, strength)

    if preserve_edges:
        filtered_values[0] = values[0]
        filtered_values[-1] = values[-1]
        if len(filtered_values) > 4:
            filtered_values[1] = (filtered_values[0] + filtered_values[1]) / 2.0
            filtered_values[-2] = (filtered_values[-1] + filtered_values[-2]) / 2.0

    return filtered_values


def mean_average(values, strength):
    """Compute the arithmetic mean, the sum of the elements along the axis
    divided by the number of elements.

    :example:
        >>> # Run a mean average on a randomly generated list of 50 values
        ... import numpy
        ... import core
        ...
        ... values = numpy.random.uniform(low=1.2, high=65.7, size=(70,))
        ... filtered_values = core.mean_average(values, 0.2)


    :param values: List of float values to smooth.
    :type values: list
    :param strength: Determine the smooth intensity.
    :type strength: float
    :return: Smoothed values
    :rtype: list
    """

    frames = (int(strength * 10)) + 1
    filtered_values = [0] * len(values)

    for itr, value in enumerate(values):
        side_values = [value]

        for frame in range(1, frames):
            t = itr - frame
            if t > 0:
                side_values.append(values[t])

            t = itr + frame
            if t < (len(values)):
                side_values.append(values[t])

        filtered_values[itr] = numpy.mean(side_values)

    return filtered_values


def gaussian(values, sigma):
    """One-dimensional Gaussian filter.

    Use scipy.gaussian_filter1d()

    :example:
        >>> # Run a gaussian filter on a randomly generated list of 50 values
        ... import numpy
        ... import core
        ...
        ... test_values = numpy.random.uniform(low=0.5, high=45.3, size=(50,))
        ... filtered_values = smooth_tool.gaussian(test_values, 1)

    :param values: List of float values to smooth.
    :type values: list
    :param sigma: Standard deviation for Gaussian kernel.
    :type sigma: int
    :return: Smoothed values
    :rtype: list
    """
    if sigma == 0:
        return values
    return list(scipy.ndimage.filters.gaussian_filter1d(values, sigma))


def moving_average(values, win_size=10):
    """Given a sequence {a_i}_(i=1)^N, an n-moving average is a new sequence
    {s_i}_(i=1)^(N-n+1) defined from the a_i by taking the arithmetic mean
    of subsequences of n terms, s_i=1/nsum_(j=i)^(i+n-1)a_j.

    :example:
        >>> # Run a moving average filter on a randomly generated list of 50 values
        ... import numpy
        ... import core
        ...
        ... test_values = numpy.random.uniform(low=0.5, high=45.3, size=(50,))
        ... filtered_values = core.moving_average(test_values, 10)

    :param values: List of float values to smooth.
    :type values: list
    :param win_size: Sample window, defaults to 10
    :type win_size: int, optional
    :return: Smoothed values
    :rtype: list
    """

    filtered_values = [values[0]]
    for i, v in enumerate(values[1 : len(values) - 1]):
        current_range = values[i : i + win_size]
        sum = math.fsum(current_range)
        new_value = sum / len(current_range)
        filtered_values.append(new_value)

    filtered_values.append(values[-1])

    return filtered_values


def savitzky_golay(values, win_size=10, order=2, derivative=0):
    """The Savitzky-Golay filter removes high frequency noise from data.
    The Savitzky-Golay is a type of low-pass filter, particularly suited for
    smoothing noisy data. The main idea behind this approach is to make for
    each point a least-square fit with a polynomial of high order over a
    odd-sized window centered at the point:
        https://www.wire.tu-bs.de/OLDWEB/mameyer/cmr/savgol.pdf

    :example:
        >>> # Run a savitzky-golay filter on a randomly generated list of 50 values
        ... import numpy
        ... import core
        ...
        ... test_values = numpy.random.uniform(low=0.5, high=45.3, size=(50,))
        ... filtered_values = core.savitzky_golay(test_values, 10)

    :param values: List of float values to smooth.
    :type values: list
    :param win_size: Sample window, defaults to 10
    :type win_size: int, optional
    :param order: Order of the polynomial used in the filtering (Needs to be less then win_size-1), defaults to 2
    :type order: int, optional
    :param derivative: Order of the derivative to compute (0 means only smoothing), defaults to 0
    :type derivative: int, optional
    :return: Smoothed values
    :rtype: list
    """

    values_array = numpy.array(values[0:])
    order_range = range(numpy.abs(numpy.int(order)) + 1)
    half_win_size = ((numpy.abs(numpy.int(win_size))) - 1) // 2

    matrix = numpy.mat(
        [
            [j ** i for i in order_range]
            for j in range(-half_win_size, half_win_size + 1)
        ]
    )
    coeff = numpy.linalg.pinv(matrix).A[derivative]

    first_value = values_array[0] - numpy.abs(
        values_array[1 : half_win_size + 1][::-1] - values_array[0]
    )
    last_value = values_array[-1] + numpy.abs(
        values_array[-half_win_size - 1 : -1][::-1] - values_array[-1]
    )

    join_array = numpy.concatenate((first_value, values_array, last_value))

    return list(numpy.convolve(coeff, join_array, mode="valid"))
