#!/usr/bin/env python3

import re
import os
import json

from .path_manager import PathManager


class GameDialogue:
	def __init__(self):
		allPaths = PathManager.get_paths()

		self.dialogicDir = allPaths["game"]["dialogic"]
		self.gameDataDir = allPaths["game"]["meta_dir"]

	def SyncDialogueToMapData(self) -> None:

		timeLineNames: set = set()
		mapDataFilePaths: set = set()

		# timeLineNames
		for timeLineFile in os.listdir(self.dialogicDir):
			if timeLineFile.endswith("json"):
				with open(os.path.join(self.dialogicDir, timeLineFile), "r") as f:
					timeLineNames.add(json.load(f)["metadata"]["name"])

		# mapDataFilePaths
		for mapDir in os.listdir(self.gameDataDir):
			mapDirPath: str = os.path.join(self.gameDataDir, mapDir)
			if re.match("zone_\d+", mapDir, re.IGNORECASE) and os.path.isdir(mapDirPath):

				mapDataFilePath: str = os.path.join(mapDirPath, mapDir + ".json")
				if os.path.isfile(mapDataFilePath):
					mapDataFilePaths.add(mapDataFilePath)

		# now sync data
		for mapDataFilePath in mapDataFilePaths:

			zoneDialogues: dict = dict()
			for timeLineName in timeLineNames:
				mapName: str = os.path.splitext(os.path.basename(mapDataFilePath))[0]
				if re.match(f"{mapName}-\d+", timeLineName, re.IGNORECASE):
					# gid = timeLineName
					zoneDialogues[timeLineName.split("-")[1]] = timeLineName

			if len(zoneDialogues) > 0:

				edited: bool = False
				mapData: dict = dict()

				with open(mapDataFilePath, "r") as f:
					mapData = json.load(f)

					for editorName in mapData:
						if re.match("\d+-\w+", editorName):
							gid: str = editorName.split("-")[0]
							if gid in zoneDialogues:
								mapData[editorName]["dialogue"] = zoneDialogues[gid]
								edited = True

				if edited and len(mapData) > 0:
					with open(mapDataFilePath, "w") as f:
						json.dump(mapData, f, indent="\t")

