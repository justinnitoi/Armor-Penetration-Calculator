"""Runs the offline test suite. Use the same Python 2.7 the build uses:

    python2.7 tests/run_tests.py

or `python build/build.py test`. Needs network access once, to download the
pinned stock gun_marker_ctrl.py into tests/.cache/ (see stock.py); without it
the tests that need the stock code are skipped.
"""

import os
import sys
import unittest

if sys.version_info[:2] != (2, 7):
    sys.exit("The tests run on Python 2.7, like the game client (got {}).".format(sys.version.split()[0]))

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TESTS_DIR)
sys.dont_write_bytecode = True  # never leave .pyc files next to the mod sources

import support  # noqa: E402

support.setup()


def main():
    suite = unittest.defaultTestLoader.discover(TESTS_DIR, pattern="test_*.py", top_level_dir=TESTS_DIR)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if support.STOCK is None:
        sys.stderr.write("WARNING: stock gun_marker_ctrl.py unavailable; stock-dependent tests skipped.\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
