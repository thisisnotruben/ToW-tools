#!/bin/bash

PEOJECT_DIR="$(dirname $(readlink -f "$0"))"

QUEST_MAKER="/content_maker/content_main.py"

$PEOJECT_DIR$QUEST_MAKER $@
