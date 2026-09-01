import math

_SIX_SQRT_2 = 6.0 * math.sqrt(2.0)


def gaussian_probability(avg_pen, armor_val):
    """Returns probability of penetration accoring to a normal distributionw with 3 SD of 0.25 * avg_pen"""
    min_pen = avg_pen * 0.75
    max_pen = avg_pen * 1.25

    if armor_val <= min_pen:
        return 100.0
    if armor_val >= max_pen:
        return 0.0

    # z-score / sqrt(2), i.e. 12 * (armor_val - avg_pen) / (avg_pen * sqrt(2))
    # If 25% is the 3-sigma point: avg_pen * 0.25 = 3 SD, so SD = avg_pen / 12.
    z_arg = _SIX_SQRT_2 * (armor_val - avg_pen) / avg_pen

    # Cumulative Distribution Function (CDF)
    # P(pen < armor)
    phi = 0.5 * (1.0 + math.erf(z_arg))

    # get area to the right P(pen > armor)
    prob = (1.0 - phi) * 100

    return prob

def arccos(cosine_value):
    return math.degrees(math.acos(cosine_value))
