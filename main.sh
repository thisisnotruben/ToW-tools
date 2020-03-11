#!/bin/bash

"$(dirname $(readlink -f "$0"))"/exporters/main.py $@zz
