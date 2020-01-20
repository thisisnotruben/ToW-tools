#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import os
import sys
import enum
import json
import tiled_exporter
import db_exporter
import archive_maker
import image_editor


class Commands(enum.Enum):
    EXPORT_MAP = enum.auto()
    EXPORT_META = enum.auto()
    EXPORT_MAP_META = enum.auto()
    EXPORT_TILESETS = enum.auto()
    EXPORT_ALL_TILED = enum.auto()
    EXPORT_DATABASES = enum.auto()
    EXPORT_ALL = enum.auto()
    DEBUG_MAP = enum.auto()
    MAKE_DEBUG_TILESETS = enum.auto()
    MAKE_32_TILESETS = enum.auto()
    BACKUP = enum.auto()
    HELP = enum.auto()


def show_commands():
    print("--> COMMANDS:")
    for c in Commands:
        print(" |-> ", c.name)
    print("--> COLORS:")
    for c in image_editor.Color:
        print(" |-> ", c.name)
    print("--> FONTS:")
    for f in image_editor.Font:
        print(" |-> ", f.name)


argv = sys.argv
if len(argv) != 3:
    print("--> NEED ARGS TO RUN $ (PATHS) (COMMAND)")
    show_commands()
    exit(1)
    
elif not argv[2] in [c.name for c in Commands]:
    print("--> UNKNOWN COMMAND: (%s)" % argv[2])
    show_commands()
    exit(1)

command = Commands[argv[2]]

data_paths = {"db":"", "tiled":"", "archive":""}
with open(argv[1], "r") as f:
    data_paths = json.load(f)
    for file_path in data_paths:
        if file_path != "root":
            data_paths[file_path] = os.path.join(data_paths["root"], data_paths[file_path])

db = db_exporter.DBExporter(data_paths["db"])
tiled = tiled_exporter.TiledExporter(data_paths["tiled"])
archive = archive_maker.Archiver(data_paths["archive"])

if command == Commands.EXPORT_MAP:
    tiled.export_map()

elif command == Commands.EXPORT_META:
    tiled.export_meta()

elif command == Commands.EXPORT_MAP_META:
    tiled.export_map()
    tiled.export_meta()
    
elif command == Commands.EXPORT_TILESETS:
    if tiled.is_debugging():
        tiled.debug_map()
    tiled.export_tilesets()

elif command == Commands.EXPORT_ALL_TILED:
    if tiled.is_debugging():
        tiled.debug_map()
    tiled.export_tilesets()
    tiled.export_map()
    tiled.export_meta()

elif command == Commands.EXPORT_DATABASES:
    db.export_databases()

elif command == Commands.EXPORT_ALL:
    if tiled.is_debugging():
        tiled.debug_map()
    tiled.export_tilesets()
    tiled.export_map()
    tiled.export_meta()
    db.export_databases()

elif command == Commands.DEBUG_MAP:
    tiled.debug_map()

elif command == Commands.MAKE_DEBUG_TILESETS:
    if tiled.is_debugging():
        tiled.debug_map()
    tiled.make_debug_tilesets()

elif command == Commands.MAKE_32_TILESETS:
    if tiled.is_debugging():
        tiled.debug_map()
    tiled.make_32_tilesets()

elif command == Commands.BACKUP:
    archive.backup()

elif command == Commands.HELP:
    show_commands()
