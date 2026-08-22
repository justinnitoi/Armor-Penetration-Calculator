from APCalculator.debug import log


try:
    from gui.aslainMenu import g_modsSettingsApi, templates  # type: ignore
    import APCalculator.settings_gui.aslain_settings

    log("Using aslain's settings api.")
except ImportError:
    # There is no aslain settings library so we try legacy

    try:
        from gui.modsSettingsApi import g_modsSettingsApi, templates  # type: ignore
        import APCalculator.settings_gui.legacy_settings

        log("Using the legacy settings api.")
    except ImportError:
        # There is no legacy settings library so we don't show the settings gui
        log("There is no settings api so no settings gui has been created.")
