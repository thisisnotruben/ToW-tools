#!/bin/bash

QT_EXT=".ui"

for file in *$QT_EXT; do
    
    py_file=$(basename -s $QT_EXT $file).py
    
    pyuic5 -x $file -o $py_file

    echo "Made: "$py_file
    
done
