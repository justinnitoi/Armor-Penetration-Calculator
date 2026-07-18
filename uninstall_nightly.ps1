
$DEST = "C:\Program Files\World_of_Tanks_NA\res_mods\2.3.0.0\scripts\client\gui\mods"
$IMAGE_DEST = "C:\Program Files\World_of_Tanks_NA\res_mods\2.3.0.0\gui\pademinune"

Remove-Item $DEST/mod_armor_pen_calculator.pyc -Force
Remove-Item $DEST/pade_constants.pyc -Force
Remove-Item $DEST/pade_gui.pyc -Force
Remove-Item $DEST/pade_config.pyc -Force
Remove-Item $DEST/pade_track.pyc -Force


Remove-Item $IMAGE_DEST\crosshair-16-green.png -Force
Remove-Item $IMAGE_DEST\crosshair-16-orange.png -Force
Remove-Item $IMAGE_DEST\crosshair-16-red.png -Force

Write-Output "Removed all 5 nightly branch files from '$DEST'"
