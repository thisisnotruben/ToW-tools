#!/bin/bash

# if using TERMINAL,
# add to tow_tool.desktop:
# "Terminal=true"
# then:
# sudo cp tow_tool.desktop /usr/share/applications/

PEOJECT_DIR="$(dirname $(readlink -f "$0"))"

TERMINAL="/core/main.py"
GUI="/gui/gui_core_main.py"

$PEOJECT_DIR$GUI $@
