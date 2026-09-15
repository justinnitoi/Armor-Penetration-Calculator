from ap_calculator.debug import VERSION, log

DISCORD_URL = "https://discord.gg/PrzqyneRXv"
DONATE_URL = "https://ko-fi.com/pademinune"
MOD_LINKAGE = "AP_Calculator_2"

try:
    from . import aslain_settings

    log("Using aslain's settings api.")
except ImportError:
    # There is no aslain settings library so we try legacy

    try:
        from . import legacy_settings

        log("Using the legacy settings api.")
    except ImportError:
        # There is no legacy settings library so we don't show the settings gui
        log("There is no settings api so no settings gui has been created.")
