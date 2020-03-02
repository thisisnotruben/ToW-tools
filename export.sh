#!/bin/bash

ROOT_DIR=/home/rubsz/tiled/Tides_of_War/non_map/scripts/
DATA=paths/paths.json
EXEC=exporters/main.py

$ROOT_DIR$EXEC $ROOT_DIR$DATA $@
