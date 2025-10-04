import numpy as np

rng = np.random.default_rng()


def skew(interval: float):
    # generating uniform random number is WAY faster in numpy than in standard lib,
    # and it really makes a difference here
    return rng.uniform(0.9 * interval, 1.1 * interval)
