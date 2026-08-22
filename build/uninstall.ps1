
$DEST = "C:\Program Files\World_of_Tanks_NA\res_mods\2.3.1.3\scripts\client\gui\mods"

Remove-Item $DEST/mod_armor_pen_calculator.pyc -Force
Remove-Item $DEST/pade_constants.pyc -Force
Remove-Item $DEST/pade_gui.pyc -Force
Remove-Item $DEST/pade_config.pyc -Force
Remove-Item $DEST/mod_pade_settings_gui.pyc -Force

Write-Output "Removed all 6 main branch files from '$DEST'"
