#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import enum
import game_db
import image_editor
import path_manager
import tiled_manager
import asset_manager
import archive_manager


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
    MAKE_32_DEBUG_TILESETS = enum.auto()
    MAKE_ICON_ATLAS = enum.auto()
    MAKE_SPRITE_ICONS = enum.auto()
    MAKE_SPRITE_DEATHS = "OPTIONAL ARG: PNG FILE PATH"
    BACKUP = enum.auto()
    HELP = enum.auto()
    QUIT = enum.auto()


class Main:
    def __init__(self, master_path):
        data_paths = path_manager.PathManager.get_paths()

        self.db = game_db.GameDB(data_paths["db"])
        self.tiled = tiled_manager.Tiled(data_paths["tiled"])
        self.archive = archive_manager.Archiver(data_paths["archive"])
        self.asset = asset_manager.AssetManager(data_paths["asset"])

    @staticmethod
    def show_commands():
        print("--> COMMANDS:")
        for command in Commands:
            print(" |-> ", command.name)
            if type(command.value) == str:
                print("    \*-> ", command.value)
        print("\n--> COLORS:")
        for color in image_editor.Color:
            print(" |-> ", color.name)
        print("\n--> FONTS:")
        for font in image_editor.Font:
            print(" |-> ", font.name)

    def execute_command(self, command, *arg):
        if not command in [c.name for c in Commands]:
            print("--> UNKNOWN COMMAND: (%s)\n--> TYPE HELP FOR ALL COMMANDS" %
                  command)
            return

        command = Commands[command]

        if command == Commands.EXPORT_MAP:
            self.tiled.export_map()

        elif command == Commands.EXPORT_META:
            self.tiled.export_meta()

        elif command == Commands.EXPORT_MAP_META:
            self.tiled.export_map()
            self.tiled.export_meta()

        elif command == Commands.EXPORT_TILESETS:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.export_tilesets()

        elif command == Commands.EXPORT_ALL_TILED:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.export_tilesets()
            self.tiled.export_map()
            self.tiled.export_meta()

        elif command == Commands.EXPORT_DATABASES:
            self.db.export_databases()

        elif command == Commands.EXPORT_ALL:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.export_tilesets()
            self.tiled.export_map()
            self.tiled.export_meta()
            self.db.export_databases()

        elif command == Commands.DEBUG_MAP:
            self.tiled.debug_map()

        elif command == Commands.MAKE_DEBUG_TILESETS:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.make_debug_tilesets()

        elif command == Commands.MAKE_32_TILESETS:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.make_32_tilesets()

        elif command == Commands.MAKE_32_DEBUG_TILESETS:
            if self.tiled.is_debugging():
                self.tiled.debug_map()
            self.tiled.make_32_tilesets()
            self.tiled.make_debug_tilesets()

        elif command == Commands.MAKE_ICON_ATLAS:
            self.asset.make_icon_atlas()

        elif command == Commands.MAKE_SPRITE_ICONS:
            self.tiled.make_sprite_icons()

        elif command == Commands.MAKE_SPRITE_DEATHS:
            self.asset.make_sprite_deaths(*arg)

        elif command == Commands.BACKUP:
            self.archive.backup()

        elif command == Commands.HELP:
            Main.show_commands()

        elif command == Commands.QUIT:
            exit(0)

    def main_loop(self):
        print("---TIDES OF WAR TOOL----")
        prompt_message = "\n--> ENTER COMMAND:\n~$ "
        while True:
            prompt = input(prompt_message).strip().split(" ")
            command = prompt[0].upper()
            args = prompt[1:]
            print("")
            self.execute_command(command, *args)


if __name__ == "__main__":
    Main(path_manager.PathManager.get_master_path()).main_loop()
