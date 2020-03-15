#!/bin/bash

# if using TERMINAL,
# add to tow_tool.desktop:
# "Terminal=true"
# then:
# sudo cp tow_tool.desktop /usr/share/applications/

PEOJECT_DIR="$(dirname $(readlink -f "$0"))"

TERMINAL="/exporters/main.py"
GUI="/gui/tool_gui_main.py"

$PEOJECT_DIR$GUI $@
