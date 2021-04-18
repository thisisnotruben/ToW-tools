#!/usr/bin/env python3

import re
import os
import shutil
import subprocess
from collections import Counter

from .game_db import GameDB, DataBases
from .image_editor import Color, Font, ImageEditor
from .path_manager import PathManager


class AssetManager:

	img_ext: str = ".png"
	godotImport: str = "import"
	audioExt: list = [".wav", ".ogg"]

	def __init__(self):
		self.assets: dict = dict()
		# load paths
		assets = PathManager.get_paths()
		self.assets["icon_atlas_data"] = assets["icon_atlas_data"]
		self.assets["game_character_dir"] = assets["game"]["character_dir"]
		self.assets["dev_character_dir"] = assets["dev_character_dir"]
		self.assets["sndDir"] = assets["game"]["sndDir"]
		self.assets["rawSndAssetDir"] = assets["rawSndAssetDir"]


	def make_icon_atlas(self) -> None:
		icon = self.assets["icon_atlas_data"]

		# check data integrity
		definedColorNames: list = [c.name for c in Color]
		for color in [icon["bg"], icon["grid"], icon["text"]]:
			if not color in definedColorNames:
				print("──> COLOR: (%s) NOT DEFINED FOR ICON ATLAS\n──> DEFINED COLORS:" % color)
				for color in definedColorNames:
					print(" |-> ", color)
				print("──> ABORTING")
				exit(1)

		definedFontNames: list = [f.name for f in Font]
		if not icon["font"] in definedFontNames:
			print("──> FONT: (%s) NOT DEFINED FOR ICON ATLAS\n──> DEFINED FONTS:" % icon["font"])
			for font in definedFontNames:
				print(" |-> ", font)
			print("──> ABORTING")
			exit(1)

		# make paths
		src: str = icon["path"]
		dest: str = os.path.join(os.path.dirname(icon["path"]), icon["atlas_name"])

		# make atlas attributes
		size: tuple = (int(icon["size"][0]), int(icon["size"][1]))
		hvFrames: tuple = (int(icon["hv_frames"][0]), int(icon["hv_frames"][1]))

		# make atlas
		print("──> MAKING ICON ATLAS:")
		ImageEditor.resize_image(src, dest, size)

		print(" |-> IMAGE RESIZED")
		ImageEditor.fill_bg(dest, dest, Color[icon["bg"]].value)

		print(" |-> IMAGE FILLED")
		ImageEditor.line_grid(dest, dest, hvFrames, Color[icon["grid"]].value)

		print(" |-> IMAGE GRID LINES MADE")
		ImageEditor.text_grid(dest, dest, hvFrames, Color[icon["text"]].value, Font[icon["font"]].value)

		print(" |-> IMAGE ENUMERATED")
		print("──> ICON ATLAS MADE: (%s)" % dest)

	def make_sprite_deaths(self, *orderPaths) -> None:
		# load img db
		imgData: dict = GameDB().get_frame_data()

		# determine order
		batchOrder: list = list()
		if len(orderPaths) == 0:
			batchOrder = [
				os.path.join(self.assets["game_character_dir"], f)
				for f in os.listdir(self.assets["game_character_dir"])
			]
		else:
			batchOrder = orderPaths
			for order in batchOrder:
				if not os.path.isfile(order):
					print("──> ERROR: (orderPaths) CANNOT CONTAIN DIRECTOR(Y/IES)\n──> ABORTING")
					return

		# start command
		command: str = "gimp -idf"
		# build command
		print("──> MAKING SPRITE DEATH ANIMATIONS")
		for src in batchOrder:
			if src.endswith(AssetManager.img_ext):
				# make args
				imgName: str = os.path.splitext(os.path.basename(src))[0]
				dest: str = src
				if not imgName in imgData.keys():
					print(" |-> SPRITE DOESN'T HAVE FRAME DATA, SKIPPING: (%s)" % src)
					continue

				hFrames: int = imgData[imgName]["total"]
				death_frame_start: int = hFrames - imgData[imgName]["attacking"] - 4
				# append arg
				command += ' -b \'(python-fu-death-anim-batch RUN-NONINTERACTIVE "%s" "%s" %d %d)\'' % (src, dest, hFrames, death_frame_start)

			elif len(orderPaths) != 0:
				print("──> ERROR: (orderPaths) ARG WRONG TYPE, MUST BE ABSOLUTE ADDRESS PNG FILE PATH")

		command += " -b '(gimp-quit 0)'"
		# execute command
		os.system(command)
		print("──> SPRITE DEATH ANIMATIONS MADE")

	def make_sym_links(self) -> None:
		syms_made: list = list()
		# file naming convention used
		pattern = re.compile("[0-9]+%s" % AssetManager.img_ext)
		# loop through all dirs to find hard copies and send to the game asset dir
		print("──> MAKING SYM LINKS")
		for dirpath, dirnames, filenames in os.walk(self.assets["dev_character_dir"]):
			for file_name in filenames:
				src = os.path.join(dirpath, file_name)
				if not os.path.islink(src) and re.search(pattern, file_name):
					dest = os.path.join(self.assets["game_character_dir"], file_name)
					shutil.move(src, dest)
					os.symlink(dest, src)
					syms_made.append(dest)
					print(" |-> SYM LINK MADE: (%s) -> (%s)" % (src, dest))
		print("──> ALL SYM LINKS MADE")
		return syms_made

	def exportRawAudio(self) -> None:
		print("──> EXPORTING AUDIO")

		tuples: list = GameDB().execute_query("SELECT name, rawName, assetFolder FROM AssetSnd;")
		allSoundNames: set = set()
		exported: list = list()
		sndDirs: set = set()

		found: bool = False
		for t in tuples:
			rawName: str = t[1]
			soundID: tuple = (t[0], rawName)
			allSoundNames.add(soundID)

			sndDir: str = os.path.join(self.assets["sndDir"], t[2])
			sndDirs.add(sndDir)
			if not os.path.isdir(sndDir):
				os.mkdir(sndDir)

			# export audio files
			for dirPath, dirNames, fileNames in os.walk(self.assets["rawSndAssetDir"]):
				for fileName in fileNames:
					if rawName == fileName:

						ext: str = os.path.splitext(fileName)[1]
						src: str = os.path.join(dirPath, rawName)
						dest: str = ""

						if ext == AssetManager.audioExt[1]: # ogg
							dest = os.path.join(sndDir, t[0] + AssetManager.audioExt[0])
							self._exportToWAV(src, dest)
						else:
							dest = os.path.join(sndDir, t[0] + ext)
							shutil.copy(src, dest)

						exported.append(soundID)


		# find stray files
		foundFiles: set = set()
		for sndDir in sndDirs:
			for fileName in os.listdir(sndDir):

				if AssetManager.godotImport not in fileName \
				and any(ext in fileName for ext in AssetManager.audioExt):
					foundFiles.add(os.path.splitext(fileName)[0])

		# display results
		for name, rawName in allSoundNames - set(exported):
			print(" |-> COULDN'T FIND: %s" % f"{name}: ".ljust(15) + rawName)

		allSoundNames = set([s[0] for s in allSoundNames])
		for fileName in allSoundNames - foundFiles:
			print(f" |-> STRAY FILE FOUND IN PROJECT: {fileName}")

		counter: Counter = Counter(exported)
		for k, v in counter.items():
			if v > 1:
				print(" |-> DUPLICATE FOUND IN ASSET POOL: %s" % f"{k[0]}: ".ljust(15) + k[1])

		print("──> ALL AUDIO EXPORTED")

	def _exportToWAV(self, src: str, dest: str):
		command: str = f"ffmpeg -i {src} {dest}"
		subprocess.call(command, shell=True)

