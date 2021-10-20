#!/usr/bin/env python3

import os
import sys
import enum

from core.game_db import GameDB
from core.image_editor import Color, Font
from core.tiled_manager import Tiled
from core.asset_manager import AssetManager
from core.archive_manager import Archiver
from core.game_dialogue import GameDialogue


class Commands(enum.Enum):
	EXPORT_MAPS = "OPTIONAL ARG: (FILE_PATH: *.tmx files) || NONE: ALL MAPS"
	EXPORT_TILESETS = enum.auto()
	EXPORT_ALL_TILED = enum.auto()
	EXPORT_DATABASES = enum.auto()
	EXPORT_CONTENT = "ARGS: (contentFilePaths)"
	EXPORT_QUEST = "ARGS: (questFilePaths)"
	EXPORT_NAMEDB = enum.auto()
	EXPORT_AUDIO = enum.auto()
	EXPORT_USED_GID = enum.auto()
	EXPORT_TILE_CSV = enum.auto()
	SET_CHAR_PROP = enum.auto()
	DEBUG_MAP = enum.auto()
	MAKE_DEBUG_TILESETS = enum.auto()
	MAKE_32_TILESETS = enum.auto()
	MAKE_32_DEBUG_TILESETS = enum.auto()
	MAKE_ICON_ATLAS = enum.auto()
	MAKE_SPRITE_ICONS = enum.auto()
	MAKE_SPRITE_DEATHS = "OPTIONAL ARG: (FILE_PATH)"
	MAKE_SYM_LINKS = enum.auto()
	MAKE_LID = "OPTIONAL ARGS: (ALL: ALL SPRITES) || (FILE_PATH: SPECIFIC SPRITE) || (NONE: SPRITES FROM SYM-LINKS)"
	SYNC_DIALOGUE = enum.auto()
	BACKUP = enum.auto()
	HELP = enum.auto()
	QUIT = enum.auto()


class Main:
	def __init__(self):
		self.db: GameDB = GameDB()
		self.tiled: Tiled = Tiled()
		self.archive: Archiver = Archiver()
		self.asset: AssetManager = AssetManager()
		self.dialogue: GameDialogue = GameDialogue()

	@staticmethod
	def show_commands():
		print("──> COMMANDS:")
		for command in Commands:
			print(" ├─", command.name)
			if type(command.value) == str:
				print("    └─> ", command.value)
		print("\n──> COLORS:")
		for color in Color:
			print(" ├─", color.name)
		print("\n──> FONTS:")
		for font in Font:
			print(" ├─> ", font.name)

	def execute_command(self, command, *arg):
		if not command in [c.name for c in Commands]:
			print(f"──> UNKNOWN COMMAND: ({command})\n──> TYPE HELP FOR ALL COMMANDS")
			return

		command = Commands[command]

		if command == Commands.EXPORT_MAPS:
			self.tiled.export_all_maps(*arg)

		elif command == Commands.EXPORT_TILESETS:
			if self.tiled.is_debugging():
				self.tiled.debug_map()
			self.tiled.export_tilesets()
			self.tiled.exportTilesetData()

		elif command == Commands.EXPORT_ALL_TILED:
			if self.tiled.is_debugging():
				self.tiled.debug_map()
			self.tiled.export_tilesets()
			self.tiled.export_all_maps()
			self.tiled.exportTilesetData()

		elif command == Commands.EXPORT_DATABASES:
			self.db.export_databases()

		elif command == Commands.EXPORT_CONTENT:
			self.db.export_character_content(*arg)

		elif command == Commands.EXPORT_QUEST:
			self.db.export_quest_content(*arg)

		elif command == Commands.EXPORT_NAMEDB:
			self.db.exportScript()

		elif command == Commands.EXPORT_AUDIO:
			self.asset.exportRawAudio()

		elif command == Commands.EXPORT_USED_GID:
			self.tiled.exportUsedTileGid()

		elif command == Commands.EXPORT_TILE_CSV:
			self.tiled.exportCsvs()

		elif command == Commands.SET_CHAR_PROP:
			self.tiled.setCharacterTilesetProperties()

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
			self.tiled.make_sprite_icons(*arg)

		elif command == Commands.MAKE_SPRITE_DEATHS:
			self.asset.make_sprite_deaths(*arg)

		elif command == Commands.MAKE_SYM_LINKS:
			self.asset.make_sym_links()

		elif command == Commands.MAKE_LID:
			sprites = self.asset.make_sym_links()
			if len(arg) > 0:
				if arg[0] == "ALL":
					# ALL
					self.tiled.make_sprite_icons()
					self.asset.make_sprite_deaths()
					sprites = []
				else:
					# FILE PATHS
					sprites = arg
			if len(sprites) > 0:
				self.tiled.make_sprite_icons(*sprites)
				self.asset.make_sprite_deaths(*sprites)

		elif command == Commands.SYNC_DIALOGUE:
			self.dialogue.SyncDialogueToMapData()

		elif command == Commands.BACKUP:
			self.archive.backup()

		elif command == Commands.HELP:
			Main.show_commands()

		elif command == Commands.QUIT:
			exit(0)

	def main_loop(self):
		print("────TIDES OF WAR TOOL────")
		prompt_message: str = "\n──> ENTER COMMAND:\n~$ "
		while True:
			prompt = input(prompt_message).strip().split(" ")
			command = prompt[0].upper()
			args = prompt[1:]
			print("")
			self.execute_command(command, *args)


if __name__ == "__main__":
	Main().main_loop()
