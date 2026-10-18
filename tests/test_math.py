import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "res", "scripts", "client")
)

from ap_calculator.core.ap_math import arccos, gaussian_probability  # noqa: E402


class GaussianProbabilityTest(unittest.TestCase):
    def test_outside_the_25_percent_band_is_certain(self):
        self.assertEqual(gaussian_probability(200.0, 150.0), 100.0)
        self.assertEqual(gaussian_probability(200.0, 250.0), 0.0)

    def test_average_pen_is_a_coin_flip(self):
        self.assertAlmostEqual(gaussian_probability(200.0, 200.0), 50.0)

    def test_symmetric_and_decreasing(self):
        low = gaussian_probability(200.0, 190.0)
        high = gaussian_probability(200.0, 210.0)
        self.assertAlmostEqual(low + high, 100.0)
        self.assertGreater(low, high)

    def test_one_sigma(self):
        # SD is avg_pen / 12, so one SD above average leaves ~15.87%
        self.assertAlmostEqual(gaussian_probability(120.0, 130.0), 15.865, places=2)

    def test_arccos(self):
        self.assertAlmostEqual(arccos(0.5), 60.0)


if __name__ == "__main__":
    unittest.main()
