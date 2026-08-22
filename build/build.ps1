
$DEST = "C:\Program Files\World_of_Tanks_NA\res_mods\2.3.1.3\scripts\client\gui\mods"

New-Item -ItemType Directory -Force -Path "bin" | Out-Null
New-Item -ItemType Directory -Force -Path $DEST | Out-Null

python27 -m py_compile src/mod_armor_pen_calculator.py
Move-Item -Force src/mod_armor_pen_calculator.pyc bin/

python27 -m py_compile src/pade_constants.py
Move-Item -Force src/pade_constants.pyc bin/

python27 -m py_compile src/pade_gui.py
Move-Item -Force src/pade_gui.pyc bin/

python27 -m py_compile src/pade_config.py
Move-Item -Force src/pade_config.pyc bin/

python27 -m py_compile src/mod_pade_settings_gui.py
Move-Item -Force src/mod_pade_settings_gui.pyc bin/

Copy-Item bin/mod_armor_pen_calculator.pyc $DEST
Copy-Item bin/pade_constants.pyc $DEST
Copy-Item bin/pade_gui.pyc $DEST
Copy-Item bin/pade_config.pyc $DEST
Copy-Item bin/mod_pade_settings_gui.pyc $DEST -Force


Write-Output "Compiled and copied main branch mod files to '$DEST'"
