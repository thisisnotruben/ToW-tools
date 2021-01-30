#!/bin/bash

VIEW_DIRS=("./content_maker/views/" "./exporter/views/")
QT_EXT=".ui"
PY_EXT=".py"

for path in "${VIEW_DIRS[@]}"; do

	for src in $path*$QT_EXT; do

		dest=$(dirname $src)/$(basename -s $QT_EXT $src)$PY_EXT

		pyuic5 -x $src -o $dest

		echo "Made: "$dest
			
	done

done
