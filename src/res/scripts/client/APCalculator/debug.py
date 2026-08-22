from APCalculator.APconstants import VERSION


def log(message):
    """Logs a message with the mod's prefix and version."""
    print("AP Calculator {}: {}".format(VERSION, message))
