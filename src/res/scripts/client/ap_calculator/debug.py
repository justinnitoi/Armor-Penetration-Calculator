import traceback

VERSION = "2.2.1"

# Each distinct error is logged in full once; repeats only bump a counter, so an
# error raised every frame from a game-loop hook can't flood python.log.
_MAX_DISTINCT_ERRORS = 20
_error_counts = {}


def log(message):
    """Logs a message with the mod's prefix and version."""

    print("[AP Calculator {}] {}".format(VERSION, message))


def log_exception(where):
    """Call from an except block: logs the current exception with its
    traceback the first time it happens at `where`, and silently counts
    repeats after that."""
    try:
        trace = traceback.format_exc()
        key = (where, trace.strip().splitlines()[-1])
        if key in _error_counts:
            _error_counts[key] += 1
        elif len(_error_counts) < _MAX_DISTINCT_ERRORS:
            _error_counts[key] = 1
            log("Error in {} (further repeats not logged):\n{}".format(where, trace))
    except Exception:
        pass
