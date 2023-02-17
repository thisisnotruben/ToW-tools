#!/usr/bin/env python3

import os
import re
import csv
import json
import shutil
import xml.etree.ElementTree as ET
from distutils.util import strtobool
from typing import *

from .game_db import GameDB, DataBases
from .image_editor import ImageEditor, Color
from .path_manager import PathManager


class Tiled:

	img_ext: str = ".png"
	map_ext: str = ".tmx"
	tileset_ext = ".tsx"
	temp_dir: str = "debugging_temp"
	special_units: list = ["critter", "aberration"]
	cell_size: int = 16

	def __init__(self):
		self.tiled: dict = dict()
		self.game: dict = dict()
		self.debug: dict = dict()
		self.tilesets_32: list = list()
		data = PathManager.get_paths()
		self.tiled = data["tiled"]
		self.tiled["hierarch"] = data["tilesetHierarch"]
		self.tiled["32hTilesets"] = data["32hTilesets"]
		self.game = data["game"]
		self.debug = data["debug"]
		self.tilesets_32 = data["32"]

	@staticmethod
	def _debugMapMoveFiles(rootDir: str, destDir: str) -> None:
		for tileset in os.listdir(rootDir):
			if tileset.endswith(Tiled.img_ext):
				src = os.path.join(rootDir, tileset)
				shutil.copy(src, destDir)

	@staticmethod
	def _getCenterPos(pos: tuple=(), size: tuple=()) -> tuple:
		offset = round(float(Tiled.cell_size) / 2.0)
		x = int(round((int(pos[0]) + int(size[0]) / 2.0) / float(Tiled.cell_size)) * float(Tiled.cell_size))
		x += offset
		y = int(pos[1]) + offset
		return (int(x), int(y))

	@staticmethod
	def _writeXml(tree, dest: str) -> None:
		tree.write(dest, encoding="UTF-8", xml_declaration=True)

	@staticmethod
	def _formatName(unitMeta: dict, unitAtts: dict) -> str:
		baseName: str = ""
		if "name" in unitAtts:
			baseName = unitAtts["name"]
		elif "template" in unitAtts:
			baseName = unitAtts["template"].split("/")[-1].split(".")[0]
		elif bool(unitMeta):
			baseName = unitMeta[unitAtts["id"]]["img"].split("-")[0]
		return "%s-%s" % (unitAtts["id"], baseName)

	def _getCharacterAttributes(self, root) -> dict:
		masterDict: dict = dict()
		tilesets: dict = dict()

		os.chdir(self.tiled["map_dir"])

		for item in root.findall("tileset"):
			if "character" in item.get("source"):
				tilesets[int(item.get("firstgid"))] = item.get("source")

		for item in root.findall("group/objectgroup[@name='characters']/object"):
			if "template" in item.keys():
				continue

			characterID: int = int(item.get("gid"))
			characterTilesetID: int = -1
			for tilesetID in tilesets:
				if characterID >= tilesetID:
					characterTilesetID = tilesetID

			characterAttr: dict = dict()
			# set default attributes from tileset
			for characterItem in ET.parse(tilesets[characterTilesetID]).getroot().findall("tile[@id]"):
				if int(characterItem.get("id")) == characterID - characterTilesetID:

					characterAttr["img"] = characterItem.find("image").get("source")
					for characterProperty in characterItem.findall("properties/property"):
						characterAttr[characterProperty.get("name")] = characterProperty.get("value")

			# set map character attributes if set
			for characterProperty in item.findall("properties/property"):
				characterAttr[characterProperty.get("name")] = characterProperty.get("value")

			masterDict[item.get("id")] = characterAttr
		return masterDict

	def _getCharacterNames(self, editorNames: bool, root) -> dict:
		unitMeta: dict = self._getCharacterAttributes(root)
		names: dict = dict()

		for item in root.findall("group/objectgroup[@name='characters']/object"):
			name: str = ""
			if editorNames:
				name = Tiled._formatName(unitMeta, item.attrib)
			elif "name" in item.keys():
				name = item.get("name")
			elif "template" not in item.keys():
				name = unitMeta[item.get("id")]["name"]
			names[item.get("id")] = name

		return names

	def _getUnitPaths(self, root) -> dict:
		unitsPaths: dict = dict()
		spawnPos: dict = self._getUnitSpawnLocs(root)

		for item in root.findall("group/objectgroup[@name='paths']/object"):
			if "name" not in item.keys() and not item.get("name").isnumeric():
				print(f"──> NO NAME SET IN PATH-ID: {item.get('id')}\n──> NAME NEEDS TO BE UNIT-ID\n──> SKIPPING")
				continue
			elif item.get("name") not in spawnPos.keys():
				print(f"──> PATH NAME: {item.get('name')} DOESN'T MATCH WITH ANY CHARACTER-ID\n──> SKIPPING")
				continue

			point_origin: tuple = spawnPos[item.get("name")]
			points: list = list()

			# 'item[0]' tag is either polygon or polyline
			for p in item[0].get("points").split(" "):
				p = p.split(",")
				points.append((int(p[0]) + point_origin[0], int(p[1]) + point_origin[1]))
			unitsPaths[item.get("name")] = points
		return unitsPaths

	def _getUnitSpawnLocs(self, root) -> dict:
		spawnPos: dict = dict()

		for item in root.findall("group/objectgroup[@name='characters']/object[@width]"):
			spawnPos[item.get("id")] = Tiled._getCenterPos(
				(item.get("x"), item.get("y")), (item.get("width"), item.get("height"))
			)

		return spawnPos

	def is_debugging(self):
		return os.path.exists(os.path.join(self.tiled["map_dir"], Tiled.temp_dir))

	def debug_map(self):
		os.chdir(self.tiled["map_dir"])
		debug = True
		if os.path.exists(Tiled.temp_dir):
			Tiled._debugMapMoveFiles(Tiled.temp_dir, self.tiled["tileset_dir"])
			shutil.rmtree(Tiled.temp_dir)
			debug = False
		else:
			os.mkdir(Tiled.temp_dir)
			Tiled._debugMapMoveFiles(self.tiled["tileset_dir"], Tiled.temp_dir)
			Tiled._debugMapMoveFiles(self.tiled["debug_dir"], self.tiled["tileset_dir"])
			with open(os.path.join(Tiled.temp_dir, "README.txt"), "w") as f:
				f.write("Don't delete folder or contents of folder manually. If you do, you've done messed up.")
		print("──> MAP DEBUG OVERLAY: %s\n──> PRESS (CTRL-T) TO REFRESH IF HASN'T SHOWN" % debug)

	def make_debug_tilesets(self):
		defined_color_names = [c.name for c in Color]
		print("──> MAKING DEBUG TILESETS:")
		for tileset in os.listdir(self.tiled["tileset_dir"]):
			if tileset.endswith(Tiled.img_ext):
				# check if color is defined
				if not self.debug[tileset] in defined_color_names:
					print("──> COLOR: (%s) NOT DEFINED FOR TILESET: (%s)\n──> DEFINED COLORS:" % (self.debug[tileset], tileset))
					for color in defined_color_names:
						print(" |-> ", color)
					print("──> ABORTING")
					exit(1)
				# make paths
				src = os.path.join(self.tiled["tileset_dir"], tileset)
				dest = os.path.join(self.tiled["debug_dir"], tileset)
				# create overlay
				ImageEditor.create_overlay(src, dest, Color[self.debug[tileset]].value)
				print(" |-> TILESET MADE: (%s)" % dest)
		print("──> ALL DEBUG TILESETS MADE")

	def make_32_tilesets(self):
		print("──> MAKING 32px TILESETS:")
		for tileset in os.listdir(self.tiled["tileset_dir"]):
			if tileset in self.tilesets_32:
				# make paths
				new_file_name: str = "%s_32%s" % (os.path.splitext(tileset)[0], Tiled.img_ext)
				src: str = os.path.join(self.tiled["tileset_dir"], tileset)
				dest: str = os.path.join(self.tiled["tileset_dir"], new_file_name)
				# make 32 image
				ImageEditor.pad_height(src, dest, 16, 16)

				print(" |-> TILESET MADE: (%s)" % dest)
		print("──> ALL 32px TILESETS MADE")

	def make_sprite_icons(self, *sprite_paths):
		batch_order = []
		if len(sprite_paths) == 0:
			# get all src img paths
			batch_order = [
				os.path.join(self.game["character_dir"], img)
				for img in os.listdir(self.game["character_dir"])
				if img.endswith(Tiled.img_ext)
			]
		else:
			batch_order = sprite_paths
			# checking if input are valid files & images
			for img in batch_order:
				if not os.path.isfile(img):
					print("──> ERROR: (sprite_paths) CANNOT CONTAIN DIRECTOR(Y/IES)\n──> ABORTING")
					return
		print("──> MAKING SPRITE ICONS")
		# load img db
		img_data = GameDB().get_frame_data()
		# make character icons
		for img in batch_order:
			if img.endswith(Tiled.img_ext):
				# make paths
				src = img
				dest = os.path.join(self.tiled["character_dir"], os.path.basename(img))
				# get hv frames for current sprite
				img_name = os.path.splitext(os.path.basename(img))[0]
				if not img_name in img_data:
					print(" |-> SPRITE DOESN'T HAVE FRAME DATA: (%s)" % src)
					continue
				character_hv_frames = (img_data[img_name]["total"], 1)
				# write image
				ImageEditor.crop_frame(
					src, dest, character_hv_frames, (0, 0))
		print("──> ALL SPRITE ICONS MADE")

	def get_character_data(self) -> list:
		# loop through all map files in dir
		master_list: list = list()
		for map_file in os.listdir(self.tiled["map_dir"]):
			if map_file.endswith(Tiled.map_ext):
				# extract file paths
				self.tiled["map_file"] = os.path.join(self.tiled["map_dir"], map_file)
				self.file_name = os.path.splitext(map_file)[0]
				# get character data
				unit_data = self._getCharacterMapData()
				for unit_id in unit_data:
					master_list.append({
						"img": os.path.join(self.tiled["character_dir"], unit_data[unit_id]["img"] + Tiled.img_ext),
						"map": os.path.splitext(os.path.basename(self.tiled["map_file"]))[0],
						"race": unit_data[unit_id]["img"].split("-")[0],
						"editorName": unit_data[unit_id]["editorName"]
					})
		return master_list

	def _getCharacterMapData(self) -> dict:
		masterDict: dict = dict()
		root = ET.parse(self.tiled["map_file"]).getroot()

		editorNames: dict = self._getCharacterNames(True, root)
		gameNames: dict = self._getCharacterNames(False, root)
		unitMeta: dict = self._getCharacterAttributes(root)
		unitPatrolPaths: dict = self._getUnitPaths(root)
		spawnPos: dict = self._getUnitSpawnLocs(root)

		for item in root.findall("group/objectgroup[@name='characters']/object"):
			if "template" in item.keys():
				continue

			unitID: str = item.get("id")
			masterDict[unitID] = {
				"editorName": editorNames[unitID],
				"name": gameNames[unitID].strip(),
				"img": os.path.splitext(unitMeta[unitID]["img"])[0],
				"dialogue": "",
				"event": unitMeta[unitID]["event"] if "event" in unitMeta[unitID] else "",
				"enemy": bool(strtobool(unitMeta[unitID]["enemy"])),
				"level": int(unitMeta[unitID]["level"]),
				"dropRate": unitMeta[unitID]["dropRate"],
				"path": unitPatrolPaths[unitID] if unitID in unitPatrolPaths else [],
				"spawnPos": spawnPos[unitID]
			}

		return masterDict

	def export_tilesets(self):
		print("──> EXPORTING TILESETS")

		for directory in ["light_dir", "tileset_dir"]:
			if os.path.exists(self.game[directory]):
				shutil.rmtree(self.game[directory])
			shutil.copytree(self.tiled[directory], self.game[directory])

			print(f" |-> DIRECTORY EXPORTED: ({self.game[directory]})")

		for filename in os.listdir(self.tiled["character_dir"]):
			if filename.endswith(Tiled.tileset_ext):

				src: str = os.path.join(self.tiled["character_dir"], filename)
				dest: str = os.path.join(self.game["character_dir"], filename)
				shutil.copy(src, dest)

				print(f" |-> TILESET EXPORTED: ({dest})")
		print("──> ALL TILESETS EXPORTED")

	def _export_map(self, fileName: str):
		tree = ET.parse(self.tiled["map_file"])
		root = tree.getroot()
		editorNames: dict = self._getCharacterNames(True, root)
		spawnPos: dict = self._getUnitSpawnLocs(root)

		for item in root.findall("group/objectgroup[@name='characters']/object"):
			characterID: str = item.get("id")
			item.set("name", str(editorNames[characterID]))
			item.set("x", str(spawnPos[characterID][0]))
			item.set("y", str(spawnPos[characterID][1]))

		targetDummySize: tuple = tuple()
		for template in os.listdir(self.tiled["template_dir"]):
			if "targetDummy" in template:
				item = ET.parse(os.path.join(self.tiled["template_dir"], template)).getroot().find("object")
				targetDummySize = (int(item.get("width")), int(item.get("height")))
		if bool(targetDummySize):
			for item in root.findall("group/objectgroup[@name='target_dummys']/object"):
				spawnPos: tuple = Tiled._getCenterPos((item.get("x"), item.get("y")), targetDummySize)
				item.set("x", str(spawnPos[0]))
				item.set("y", str(spawnPos[1]))
				item.set("name", Tiled._formatName({}, item.attrib))

		for objectGroupName in ["lights", "gravesites"]:
			for item in root.findall(f"group/objectgroup[@name='{objectGroupName}']/object"):
				item.set("name", Tiled._formatName(dict(), item.attrib))

		for item in root.findall("group/objectgroup[@name='lightSpace']/object"):
			connectedLight = item.find("properties/property[@name='light']")
			name: str = item.get("id") if connectedLight is None else connectedLight.get("value")
			item.set("name", "%s-%s" % (name, item.get("width")))

		for item in root.findall(".//objectgroup[@name='quest']/object"):
			item.set("name", "%s-quest%s"
				% (item.get("id"), item.find("properties/property[@name='type']").get("value")))

		self._standardizeTilesetGroups(root)
		self._standardizeTilesets(root)

		dest: str = os.path.join(self.game["map_dir"], fileName + Tiled.map_ext)
		Tiled._writeXml(tree, dest)
		print("──> MAP: (%s) EXPORTED -> (%s)" % (fileName, dest))

	def _exportMapData(self, fileName: str):
		master_dict = self._getCharacterMapData()

		# reformat data
		reformattedDict: dict = dict()
		for unit_ID in master_dict:
			if "editorName" in master_dict[unit_ID]:
				unit_editor_name : str = master_dict[unit_ID]["editorName"]
				del master_dict[unit_ID]["editorName"]
				reformattedDict[unit_editor_name] = master_dict[unit_ID]

		destDir = os.path.join(self.game["meta_dir"], fileName)

		# main file
		dest = os.path.join(destDir, "%s.json" % fileName)
		with open(dest, "w") as outfile:
			json.dump(reformattedDict, outfile, indent="\t")

		# quest loot file
		src = os.path.join(self.tiled["map_dir"], fileName + Tiled.map_ext)
		if os.path.isfile(src):

			dest = os.path.join(destDir, "%s_questLoot.json" % fileName)
			with open(dest, "w") as outfile:
				json.dump(self._getQuestItemData(src), outfile, indent="\t")

		print("──> META: (%s) EXPORTED" % fileName)

	def export_all_maps(self, *map_paths):
		if len(map_paths) == 0:
			# if no args, then export all maps
			map_paths = []
			for map_file in os.listdir(self.tiled["map_dir"]):
				if re.match("zone_\d%s" % Tiled.map_ext , map_file):
					map_paths.append(os.path.join(self.tiled["map_dir"], map_file))

		for map_file in map_paths:
			self.tiled["map_file"] = map_file
			fileName = os.path.splitext(os.path.basename(map_file))[0]
			self._export_map(fileName)
			self._exportMapData(fileName)
			self._exportCharacterQuestDropData(map_file)

	def _standardizeTilesetGroups(self, root) -> None:
		horizontalBit: int = 0x80000000

		tilesets: dict = self._getCurrentHierarchData(root)
		hierarch: dict = self._getHierarchData()

		objectPaths: List[str] = [
			".//objectgroup[@name='transitionSigns']",
			".//objectgroup[@name='quest']"
		]

		data: Dict[ET.Element, str] = {}

		for objectPath in objectPaths:
			for objects in root.findall(objectPath):

				if "gid" not in objects.keys():
				# the case for non-tile objects like area-objects
					continue

				for gid in tilesets.keys():
					tilesetName: str = os.path.splitext(os.path.basename(tilesets[gid]["source"]))[0]
					for item in objects.findall("object"):

						tile: int = int(item.get("gid"))
						flippedH: bool = tile & horizontalBit > 0
						if flippedH:
							tile &= ~horizontalBit

						if tile >= gid and tile < gid + hierarch[tilesetName][1]:
							if flippedH:
								tile |= horizontalBit

							newTileID: int = tile - gid + hierarch[tilesetName][2]
							data[item] = str(newTileID)

		for tileObject, newId in data.items():
				tileObject.set("gid", newId)

	def _standardizeTilesets(self, root) -> None:
		horizontalBit: int = 0x80000000

		tilesets: dict = self._getCurrentHierarchData(root)
		matrices: dict = dict()
		hierarch: dict = self._getHierarchData()

		for item in root.findall("group/layer"):
			csvData = item.find("data[@encoding='csv']")
			if csvData is not None:
				matrices[item.get("name")] = [
					[int(c) for c in row if c.isdigit()]
					for row in csv.reader(csvData.text.split("\n"), delimiter=",")
					if len(row) > 0
				]

		# put it all together
		refTilesets: dict = dict()
		for gid in tilesets.keys():

			tilesetName: str = os.path.splitext(os.path.basename(tilesets[gid]["source"]))[0]
			data: dict = {
				"firstgid": hierarch[tilesetName][2],
				"tilesetName": tilesetName,
				"tiles": dict()
			}

			for layerName, matrix in matrices.items():
				data["tiles"][layerName] = set()

				for i in range(len(matrix)):
					for j in range(len(matrix[i])):

						tile: int = matrix[i][j]
						flippedH: bool = tile & horizontalBit > 0
						if flippedH:
							tile &= ~horizontalBit

						if tile >= gid and tile < gid + hierarch[tilesetName][1]:
							if flippedH:
								tile |= horizontalBit
							newTileID: int = tile - gid + hierarch[tilesetName][2]

							data["tiles"][layerName].add((i, j, newTileID))

			refTilesets[gid] = data

		# write new tiles id's to matrix
		for matrix in matrices.values():
			for data in refTilesets.values():
				for layerName, newTileIDPackets in data["tiles"].items():
					for newTileIDPacket in newTileIDPackets:
						matrices[layerName][newTileIDPacket[0]][newTileIDPacket[1]] = newTileIDPacket[2]

		# write matrix results to xml
		for item in root.findall("tileset"):
			data: dict = refTilesets[int(item.get("firstgid"))]
			item.set("firstgid", str(data["firstgid"]))
			item.set("source", "tilesets/" + data["tilesetName"] + Tiled.tileset_ext)

		for item in root.findall("group/layer"):
			csvData = item.find("data[@encoding='csv']")
			if csvData is None:
				continue

			matrixStr: str = "\n"
			for row in matrices[item.get("name")]:
				matrixStr += ",".join([str(c) for c in row]) + ",\n"
			csvData.text = matrixStr[:-2] + "\n"

		for tagName in ["characters", "lightSpace"]:
			for item in root.findall(f"group/objectgroup[@name='{tagName}']/object"):
				item.set("gid", "0")

	def _getCurrentHierarchData(self, root) -> Dict[int, Dict]:
		tilesets: Dict[int, Dict] = {}

		i: int = 1
		for item in root.findall("tileset"):
			if "tilesets" in item.get("source"):
				tilesets[int(item.get("firstgid"))] = {
					"source": item.get("source"),
					"hierarch": i,
				}
				i += 1
			else:
				root.remove(item)

		return tilesets

	def _getHierarchData(self) -> dict:
		hierarch: dict = dict()
		for tilesetName, level in self.tiled["hierarch"].items():
			tilesetPath: str = os.path.join(self.tiled["tileset_dir"], tilesetName + Tiled.img_ext)
			imgSize: tuple = ImageEditor.get_size(tilesetPath)
			cells: int = -1

			if tilesetName in self.tiled["32hTilesets"]:
				cells = imgSize[0] // 16 * imgSize[1] // 32
			else:
				cells = imgSize[0] * imgSize[1] // 16**2

			hierarch[tilesetName] = (int(level), int(cells))

		for tilesetName, dataPacket in hierarch.items():
			firstgid: int = 1
			for v in hierarch.values():
				if v[0] < dataPacket[0]:
					firstgid += v[1]

			hierarch[tilesetName] = (dataPacket[0], dataPacket[1], firstgid)

		return hierarch

	def exportTilesetData(self) -> None:
		occluderData: dict = dict()
		shaderData: dict = dict()

		for dirpath, _, filenames in os.walk(self.tiled["map_dir"]):
			for filename in filenames:
				filepath: str = os.path.join(dirpath, filename)

				if filepath.endswith(Tiled.tileset_ext):
					occluderData.update(self._getOccluderData(filepath))
					shaderData.update(self._getTileShaderData(filepath))

				elif filepath.endswith(Tiled.map_ext):
					for item in ET.parse(filepath).getroot().findall("group/objectgroup/object"):
						shaderProperty = item.find("properties/property[@name='shader']")
						if shaderProperty is not None:
							shaderData["%s-%s" % (os.path.splitext(filename)[0], item.get("id"))] = shaderProperty.get("value")

		dest: str = os.path.join(self.game["meta_dir"], "importer")
		dataPackets: list = [
			(os.path.join(dest, "tilesetLightOccluders.json"), occluderData),
			(os.path.join(dest, "tilesetAnimations.json"), self._getTileAnimData()),
			(os.path.join(dest, "tilesetShaders.json"), shaderData),
			(os.path.join(dest, "tilesetLightPos.json"), self._getLightPos())
		]

		if not os.path.isdir(dest):
			os.mkdir(dest)
		for dataPacket in dataPackets:
			with open(dataPacket[0], "w") as outfile:
				json.dump(dataPacket[1], outfile, indent="\t")

	def _getOccluderData(self, tilesetPath: str) -> dict:
		getFileName = lambda filePath: os.path.splitext(os.path.basename(filePath))[0]

		root = ET.parse(tilesetPath).getroot()
		tilesetName: str = getFileName(tilesetPath)

		master: dict = dict()
		hierarch: dict = self._getHierarchData()
		templatePaths: set = set()

		# get all tile occluder data
		for tile in root.findall("tile"):
			for item in tile.findall("objectgroup/object[@template]"):
				if "occluder" in item.get("template"):

					tileGid: int = hierarch[tilesetName][2] + int(tile.get("id"))
					master[tileGid] = {
						"templateName": getFileName(item.get("template")),
						"pos": [int(item.get("x")), int(item.get("y"))]
					}
					templatePaths.add(os.path.join(self.tiled["tileset_dir"], item.get("template")))

		# get the occluder data
		for templatePath in templatePaths:
			polygonTag = ET.parse(templatePath).getroot().find("object/polygon")
			points: list = list()
			for point in polygonTag.get("points").split(" "):
				point = point.split(",")
				points.append(int(point[0]))
				points.append(int(point[1]))
			master[getFileName(templatePath)] = points

		return master

	def _getTileAnimData(self) -> dict:
		root = ET.parse(os.path.join(self.tiled["tileset_dir"], "terrain" + Tiled.tileset_ext)).getroot()

		return {
			int(tile.get("id")) + 1: tile.get("type")
			for tile in root.findall("tile[@type]")
		}

	def _getTileShaderData(self, tilesetPath: str) -> dict:
		master: dict = dict()
		hierarch: dict = self._getHierarchData()

		for tile in ET.parse(tilesetPath).getroot().findall("tile[@id]"):
			item = tile.find("properties/property[@name='shader']")
			if item is None:
				continue

			shaderName: str = item.get("value").strip()
			if len(shaderName) > 0:
				tilesetName: str = os.path.splitext(os.path.basename(tilesetPath))[0]
				tileGid: int = hierarch[tilesetName][2] + int(tile.get("id"))
				master[tileGid] = shaderName

		return master

	def _getLightPos(self) -> dict:
		master: dict = dict()
		hierarch: dict = self._getHierarchData()

		tilesetName: str = "buildings"
		root = ET.parse(os.path.join(self.tiled["tileset_dir"], tilesetName + Tiled.tileset_ext)).getroot()

		for tile in root.findall("tile"):
			for item in tile.findall("objectgroup/object[@template]"):
				if "lightPos" in item.get("template"):

					tileGid: int = hierarch[tilesetName][2] + int(tile.get("id"))
					master[tileGid] = [int(item.get("x")), int(item.get("y"))]

		return master

	def _getQuestItemData(self, mapFilepath: str) -> Dict[Optional[str], list]:
		master: Dict[Optional[str], list] = dict()
		template: str = "properties/property[@name='%s']"

		for group in ET.parse(mapFilepath).getroot().findall(".//objectgroup[@name='quest']"):
			for item in group.findall("object"):

				value = item.find(template % "value")
				questId = item.find(template % "questId")
				interactType = item.find(template % "type")

				if value is None or questId is None or interactType is None:
					print(f"Error: {item.get('id')} in quests doesn't have all attributes")
				else:

					payload: dict = {
						"name": "%s-quest%s" % (item.get("id"), interactType.get("value").capitalize()),
						"type": interactType.get("value"),
						"value": value.get("value")
					}

					quest: Optional[str] = questId.get("value")

					if quest in master:
						master[quest].append(payload)
					else:
						master[quest] = [payload]

		return master

	def exportUsedTileGid(self) -> None:
		"""Exports all used tile GID's; optimizes tileset to way smaller file"""
		horizontalBit: int = 0x80000000
		usedGids: set = set()

		for filename in os.listdir(self.game["map_dir"]):
			if not filename.endswith(Tiled.map_ext):
				continue

			root = ET.parse(os.path.join(self.game["map_dir"], filename)).getroot()
			for item in root.findall("group/layer"):
				csvData = item.find("data[@encoding='csv']")
				if csvData is None:
					continue

				for row in csv.reader(csvData.text.split("\n"), delimiter=","):
					for gid in row:
						if gid.isdigit() and gid != "0":
							tile: int = int(gid)
							if tile & horizontalBit > 0:
								tile &= ~horizontalBit
							usedGids.add(tile)

		dest: str = os.path.join(self.game["meta_dir"], "importer", "usedGid.json")
		with open(dest, "w") as outfile:
			json.dump(sorted(list(usedGids)), outfile, indent="\t")

	def exportCsvs(self):
		for filename in os.listdir(self.game["map_dir"]):
			if not filename.endswith(Tiled.map_ext):
				continue

			tileData: dict = dict()
			root = ET.parse(os.path.join(self.game["map_dir"], filename)).getroot()

			for group in root.findall("group"):
				tileData[group.get("name")] = dict()

				for item in group.findall("layer"):
					csvData = item.find("data[@encoding='csv']")
					if csvData is not None:
						tileData[group.get("name")][item.get("name")] = [
							[int(c) for c in row if c.isdigit()]
							for row in csv.reader(csvData.text.split("\n"), delimiter=",")
							if len(row) > 0
						]

			dest: str = os.path.join(self.game["meta_dir"], "importer", os.path.splitext(filename)[0] + ".json")
			with open(dest, "w") as outfile:
				json.dump(tileData, outfile, indent="\t")

	def setCharacterTilesetProperties(self) -> None:
		"""So that all tiles in 'Tiled' have by default these defined propertiess"""

		characterAtlas: dict = {
			"enemy": {"type": "bool", "value":"false"},
			"level": {"type": "int", "value": "1"},
			"dropRate": {"type": "float", "value": "0.5"},
			"name": {"value": ""},
		}
		characterAttributes: set = set(characterAtlas.keys())

		for filename in os.listdir(self.tiled["character_dir"]):
			if filename.endswith(Tiled.tileset_ext):

				filepath: str = os.path.join(self.tiled["character_dir"], filename)
				tree = ET.parse(filepath)

				for character in tree.getroot().findall("tile"):
					characterProperties = character.find("properties")

					attributes: set = set()
					if characterProperties is None:
						characterProperties = ET.SubElement(character, "properties")
					else:
						for characterProperty in characterProperties:
							attributes.add(characterProperty.get("name"))

					for prop in characterAttributes - attributes:
						attribute = ET.SubElement(characterProperties, "property", {
							"name": prop,
							"value": characterAtlas[prop]["value"]
						})
						if "type" in characterAtlas[prop].keys():
							attribute.set("type", characterAtlas[prop]["type"])

				Tiled._writeXml(tree, filepath)

	def _exportCharacterQuestDropData(self, mapPath) -> None:

		root = ET.parse(mapPath).getroot()

		unitData: dict = self._getCharacterAttributes(root)
		editorNames: dict = self._getCharacterNames(True, root)
		exportData: dict = dict()

		for unitId, properties in unitData.items():
			for prop, questDrop in properties.items():

				if re.match("q\d+\.\d+\.\d+-d\d+", prop, re.IGNORECASE): # ex matches q1.1175.0-d0
					questId: str = prop.split("-")[0]

					if questId not in exportData.keys():
						exportData[questId] = {
							"drops": set(),
						}

					exportData[questId][editorNames[unitId]] = questDrop
					exportData[questId]["drops"].add(questDrop)

		masterDict: dict = {}
		for questId in exportData.keys():

			masterDict[questId] = {}
			for drop in exportData[questId]["drops"]:

				masterDict[questId][drop] = []
				for unitEditorName, unitDrop in exportData[questId].items():
					if unitDrop == drop:
						masterDict[questId][drop].append(unitEditorName)


		zoneName: str = os.path.splitext(os.path.basename(mapPath))[0]
		dest: str = os.path.join(self.game["meta_dir"], zoneName, "%s_questUnitDrop.json" % zoneName)
		with open(dest, "w") as outfile:
			json.dump(masterDict, outfile, indent="\t")
