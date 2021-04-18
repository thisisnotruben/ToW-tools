#!/usr/bin/env python3

import os
import re
import enum
import json
import sqlite3
from distutils.util import strtobool

from .path_manager import PathManager


class DataBases(enum.Enum):
	IMAGEDB = "image"
	ITEMDB = "item"
	SPELLDB = "spell"
	MISSILE_SPELL = "missileSpell"
	AREA_EFFECT = "areaEffect"
	LAND_MINE = "landMine"
	MODIFIER = "modifier"
	USE = "use"


class GameDB:

	content_ext = ".json"

	def __init__(self):
		paths = PathManager.get_paths()
		self.paths: dict = {
			"db_dir": paths["db_dir"],
			"db_export_path": paths["db_export_path"],
			"character_content_dir": paths["character_content_dir"],
			"quest_content_dir": paths["quest_content_dir"],
			"nameDB": paths["nameDB"]
		}
		self.database_path = paths["database"]
		self._load_db()

	def __del__(self):
		self.conn.close()

	def _load_db(self, sameThread=True):
		self.conn = sqlite3.connect(self.database_path, check_same_thread=sameThread)
		self.cursor = self.conn.cursor()

	def _export(self, data: dict, dest: str) -> None:
		with open(dest, "w") as outfile:
			json.dump(data, outfile, indent="\t")

	def get_frame_data(self) -> dict:
		master = {}
		self.cursor.execute("SELECT * FROM ImageFrames")
		for row in self.cursor.fetchall():
			master[row[0]] = {
				"total": row[1],
				"moving": row[2],
				"dying": row[3],
				"attacking": row[4]
			}
		return master

	def execute_query(self, query: str) -> list:
		# some protection for sql queries
		l = query.find("'") + 1
		r = query.rfind("'")
		if l < r:
			subString = query[l:r]
			query = query.replace(subString, subString.replace("'", "''"))
		# execute query
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def _getDB(self, query: str) -> dict:
		tuples = self.execute_query(query)
		attributeNames = [attName[0] for attName in self.cursor.description]
		return {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}

	def getModDB(self) -> dict:
		tuples = self.execute_query("SELECT * FROM modifier;")
		attributeNames = [attName[0] for attName in self.cursor.description]
		modAttributes = ["stamina", "intellect", "agility", "hpMax", \
			"manaMax", "maxDamage", "minDamage", "regenTime", "armor", \
			"weaponRange", "weaponSpeed", "moveSpeed"]

		mod = dict()
		for t in tuples:
			mod[t[0]] = {
				"durationSec": t[attributeNames.index("duration")],
				**{attribute : {
					"type": t[attributeNames.index(attribute + "Type")],
					"value": t[attributeNames.index(attribute)]
				} for attribute in modAttributes}
			}

		return mod

	def getUseDB(self) -> dict:
		tuples = self.execute_query("SELECT * FROM use;")
		attributeNames = [attName[0] for attName in self.cursor.description]
		useAttributes = ["hp", "mana", "damage"]

		use = dict()
		for t in tuples:
			use[t[0]] = {
				"totalSec": t[attributeNames.index("totalSec")],
				"repeatSec": t[attributeNames.index("repeatSec")],
				**{attribute : {
					"type": t[attributeNames.index(attribute + "Type")],
					"value": t[attributeNames.index(attribute)]
				} for attribute in useAttributes}
			}

		return use

	def getItemDB(self) -> dict:
		return self._getDB("SELECT * FROM worldobject NATURAL JOIN item;")

	def getAreaEffectDB(self) -> dict:
		return self._getDB("SELECT * FROM areaeffect;")

	def getLandMineDB(self) -> dict:
		return self._getDB("SELECT * FROM landmine NATURAL JOIN areaeffect;")

	def getSpellDB(self) -> dict:
		tuples = self.execute_query("SELECT * FROM worldobject NATURAL JOIN spell;")
		attributeNames = [attName[0] for attName in self.cursor.description]

		idxs = [
			attributeNames.index("ignoreArmor"),
			attributeNames.index("requiresTarget")
		]

		# convert intended bools to bools
		for i in range(len(tuples)):
			tuples[i] = list(tuples[i])
			for j in range(len(idxs)):
				tuples[i][idxs[j]] = tuples[i][idxs[j]] == 1

		return {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}

	def getImageDB(self) -> dict:
		tuples = self.execute_query("SELECT * FROM image;")
		attributeNames = [attName[0] for attName in self.cursor.description]

		attributeNames = list(map(
			lambda attName: attName.replace("Frames", ""),
			attributeNames)
		)

		# convert intended bools to bools
		meleeIdx = attributeNames.index("melee")
		for i in range(len(tuples)):
			tuples[i] = list(tuples[i])
			tuples[i][meleeIdx] = tuples[i][meleeIdx] == 1

		return {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}

	def getMissileSpellDB(self) -> dict:
		tuples = self.execute_query("SELECT * FROM missilespell;")
		attributeNames = [attName[0] for attName in self.cursor.description]

		# convert intended bools to bools
		idxs = [
			attributeNames.index("rotate")
		]
		for i in range(len(tuples)):
			tuples[i] = list(tuples[i])
			for j in range(len(idxs)):
				tuples[i][idxs[j]] = tuples[i][idxs[j]] == 1

		return {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}

	def export_databases(self) -> None:
		print("──> EXPORTING DATABASES")

		databases: dict = {
			DataBases.ITEMDB: self.getItemDB(),
			DataBases.SPELLDB: self.getSpellDB(),
			DataBases.IMAGEDB: self.getImageDB(),
			DataBases.MISSILE_SPELL: self.getMissileSpellDB(),
			DataBases.AREA_EFFECT: self.getAreaEffectDB(),
			DataBases.LAND_MINE: self.getLandMineDB(),
			DataBases.MODIFIER: self.getModDB(),
			DataBases.USE: self.getUseDB()
		}

		# export databases
		for db in databases.keys():
			dest = os.path.join(self.paths["db_export_path"], db.value + GameDB.content_ext)
			self._export(databases[db], dest)

			print(f" |-> DATABASE EXPORTED: ({dest})")
		print("──> ALL DATABASES EXPORTED")

	def exportScript(self) -> None:
		print("──> EXPORTING SCRIPTS")

		self.cursor.execute("SELECT name FROM sound WHERE assetfolder='ui' ORDER BY name ASC;")
		tuples: list = self.cursor.fetchall()

		definitions: str = "public const string"

		with open(self.paths["nameDB"], "r+") as nameDB:
			f: str = nameDB.read()

			m = re.search(r"public static class Sound.*\{.*\}", f, re.DOTALL | re.IGNORECASE)
			if m != None:
				result: str = m.group(0)
				result = result[result.find(definitions) + len(definitions): result.find("}")]

				names: str = ""
				for t in tuples:
					names += "\t" * 4 + f'{t[0].upper().replace(" ", "_")} = "{t[0]}",\n'
				names = names[0: -2]
				names += ";"

				f = f.replace(result, names)
			nameDB.seek(0)
			nameDB.write(f)

	@staticmethod
	def getWorldName(world_packet: list, nodePath: bool = False) -> str:
		name: str = ""

		if len(world_packet) > 0:
			delimiter: str = " | "
			name = world_packet[0]

			if delimiter in name:
				splittedName: list = name.split(delimiter)
				name = f"/root/{splittedName[1]}/zed/z1/{splittedName[0]}" \
					if nodePath else splittedName[0]
		return name

	def export_character_content(self, *contentFilePaths) -> None:
		print("──> EXPORTING CHARACTER CONTENT")

		if len(contentFilePaths) == 0:
			print(" |-> ABORTING: NO PATHS GIVEN")
			return

		for contentFile in contentFilePaths:
			with open(contentFile, "r") as infile:
				content = json.load(infile)

				# reformat json
				reformattedDict = {}
				for node in content["nodes"].keys():
					nodeDict = content["nodes"][node]
					if len(nodeDict["character"]) == 0:
						print(f" |-> CHARACTER CONTENT NOT EXPORTED: ({nodeDict})")
						continue

					# parse main
					character_name = GameDB.getWorldName(nodeDict.pop("character"))
					nodeDict["drops"] = list(map(GameDB.getWorldName, nodeDict["drops"]))
					nodeDict["spells"] = list(map(GameDB.getWorldName, nodeDict["spells"]))
					nodeDict["merchandise"] = list(map(GameDB.getWorldName, nodeDict["merchandise"]))

					# add to main dict
					reformattedDict[character_name] = nodeDict

				# export json
				fileName = os.path.splitext(os.path.basename(contentFile))[0]
				dest = os.path.join(self.paths["db_export_path"], fileName + GameDB.content_ext)
				self._export(reformattedDict, dest)
				print(f" |-> CHARACTER CONTENT EXPORTED: ({dest})")

	def export_quest_content(self, *questFilePaths) -> None:
		print("──> EXPORTING QUEST CONTENT")

		if len(questFilePaths) == 0:
			print(" |-> ABORTING: NO PATHS GIVEN")
			return

		for questFile in questFilePaths:
			with open(questFile, "r") as infile:
				content = json.load(infile)

				# reformat json
				reformattedDict: dict = {}
				for node in content["nodes"].keys():

					# quest needs to have:
					# name, at least one objective, and quest giver/completer
					nodeDict: dict = content["nodes"][node]
					if len(nodeDict["questName"].strip()) == 0 \
					or len(nodeDict["questGiver"]) == 0 \
					or len(nodeDict["questCompleter"]) == 0 \
					or len(nodeDict["objectives"].keys()) == 0:
						continue

					questName: str = nodeDict.pop("questName")

					nodeDict["questGiver"] = GameDB.getWorldName(nodeDict["questGiver"], True)
					nodeDict["questCompleter"] = GameDB.getWorldName(nodeDict["questCompleter"], True)

					nodeDict["nextQuest"] = list(map(GameDB.getWorldName, nodeDict["nextQuest"]))
					nodeDict["reward"] = list(map(GameDB.getWorldName, nodeDict["reward"]))

					# parse objective
					objectives: dict = {}
					for objective in nodeDict["objectives"].keys():
						worldObjectName: str = GameDB.getWorldName(nodeDict["objectives"][objective].pop("worldObject"))

						del nodeDict["objectives"][objective]["wildcard"]

						nodeDict["objectives"][objective]["questType"] = \
							nodeDict["objectives"][objective]["questType"].upper()

						nodeDict["objectives"][objective]["extraContent"]["reward"] = \
							GameDB.getWorldName(nodeDict["objectives"][objective]["extraContent"]["reward"])

						objectives[worldObjectName] = nodeDict["objectives"][objective]

					del nodeDict["objectives"]
					nodeDict["objectives"] = objectives

					reformattedDict[questName] = nodeDict

				# export json
				fileName = os.path.splitext(os.path.basename(questFile))[0]
				dest = os.path.join(self.paths["db_export_path"], "quest", fileName + GameDB.content_ext)
				self._export(reformattedDict, dest)

				print(f" |-> QUEST CONTENT EXPORTED: ({dest})")

