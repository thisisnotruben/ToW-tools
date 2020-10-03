#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import enum
import json
import sqlite3
import pyexcel_ods
from distutils.util import strtobool

from core.path_manager import PathManager


class DataBases(enum.Enum):
    IMAGEDB = "image"
    ITEMDB = "item"
    SPELLDB = "spell"
    MISSILE_SPELL = "missileSpell"


class GameDB:

    content_ext = ".json"

    def __init__(self):
        paths = PathManager.get_paths()
        self.paths = {
            "db_dir": paths["db_dir"],
            "db_export_path": paths["db_export_path"],
            "character_content_dir": paths["character_content_dir"],
            "quest_content_dir": paths["quest_content_dir"]
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

    def _getModAttributeNames(self) -> list:
        return ["stamina", "intellect", "agility", "hpMax", \
        "manaMax", "maxDamage", "minDamage", "regenTime", "armor", \
        "weaponRange", "weaponSpeed"]

    def _getUseAttributeNames(self) -> list:
        return ["hp", "mana", "damage"]

    def _getModBoilerPlate(self) -> dict:
        modAttributes = self._getModAttributeNames()

        return {
            "durationSec": 0,
            **{attribute : {
                "type": "FLAT",
                "value": 0 
            } for attribute in modAttributes}
        }

    def _getUseBoilerPlate(self) -> dict:
        useAttributes = self._getUseAttributeNames()

        return {
            "repeatSec": 0,
            **{attribute : {
                "type": "FLAT",
                "value": 0
            } for attribute in useAttributes}
        }

    def _setModUseDB(self, data: dict) -> dict:
        data = data.copy()

        modBp: dict = self._getModBoilerPlate()
        useBp: dict = self._getUseBoilerPlate()

        useTuples = self.execute_query("SELECT * FROM use;")
        useAttributeNames = [attName[0] for attName in self.cursor.description]
        useNameTupleIdx = [t[0] for t in useTuples]

        modTuples = self.execute_query("SELECT * FROM modifier;")
        modAttributeNames = [attName[0] for attName in self.cursor.description]
        modNameTupleIdx = [t[0] for t in modTuples]

        for datum in data.keys():

            mod = modBp.copy()
            if datum in modNameTupleIdx:
                t = modTuples[modNameTupleIdx.index(datum)]
                # set mod values
                mod["durationSec"] = t[modAttributeNames.index("duration")]
                for attName in self._getModAttributeNames():
                    mod[attName]["value"] = t[modAttributeNames.index(attName)]
                    mod[attName]["type"] = t[modAttributeNames.index(attName + "Type")]

            use = useBp.copy()
            if datum in useNameTupleIdx:
                t = useTuples[useNameTupleIdx.index(datum)]
                # set use values
                use["repeatSec"] = t[useAttributeNames.index("repeatSec")]
                for attName in self._getUseAttributeNames():
                    use[attName]["value"] = t[useAttributeNames.index(attName)]
                    use[attName]["type"] = t[useAttributeNames.index(attName + "Type")]

            data[datum]["modifiers"] = mod
            data[datum]["use"] = use

        return data

    def getItemDB(self) -> dict:
        tuples = self.execute_query("SELECT * FROM worldobject NATURAL JOIN item;")
        attributeNames = [attName[0] for attName in self.cursor.description]

        data: dict = {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}
        data = self._setModUseDB(data)
        return data

    def getSpellDB(self) -> dict:
        tuples = self.execute_query("SELECT * FROM worldobject NATURAL JOIN spell;")
        attributeNames = [attName[0] for attName in self.cursor.description]

        idxs = [
            attributeNames.index("ignoreArmor"),
            attributeNames.index("effectOnTarget"),
            attributeNames.index("requiresTarget")
        ]

        # convert intended bools to bools
        for i in range(len(tuples)):
            tuples[i] = list(tuples[i])
            for j in range(len(idxs)):
                tuples[i][idxs[j]] = tuples[i][idxs[j]] == 1

        data: dict = {t[0]: dict(zip(attributeNames[1:], t[1:])) for t in tuples}
        data = self._setModUseDB(data)
        return data

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
        tuples = self.execute_query(f"SELECT * FROM missilespell;")
        attribute_names = [attName[0] for attName in self.cursor.description]

        # convert intended bools to bools
        idxs = [
            attribute_names.index("rotate"),
            attribute_names.index("instantSpawn"),
            attribute_names.index("reverse")
        ]
        for i in range(len(tuples)):
            tuples[i] = list(tuples[i])
            for j in range(len(idxs)):
                tuples[i][idxs[j]] = tuples[i][idxs[j]] == 1

        return {t[0]: dict(zip(attribute_names[1:], t[1:])) for t in tuples}

    def export_databases(self) -> None:
        print("--> EXPORTING DATABASES")

        databases: dict = {
            DataBases.ITEMDB: self.getItemDB(),
            DataBases.SPELLDB: self.getSpellDB(),
            DataBases.IMAGEDB: self.getImageDB(),
            DataBases.MISSILE_SPELL: self.getMissileSpellDB()
        }

        # export databases
        for db in databases.keys():
            dest = os.path.join(self.paths["db_export_path"], db.value + GameDB.content_ext)
            self._export(databases[db], dest)

            print(f" |-> DATABASE EXPORTED: ({dest})")
        print("--> ALL DATABASES EXPORTED")

    @staticmethod
    def getWorldName(world_packet: list) -> str:
        if len(world_packet) > 0:
            delimiter = " | "
            name = world_packet[0]
            return name[:name.index(delimiter)] if delimiter in name else name
        return ""

    def export_character_content(self, *contentFilePaths) -> None:
        print("--> EXPORTING CHARACTER CONTENT")

        if len(contentFilePaths) == 0:
            print(" |-> ABORTING: NO PATHS GIVEN")
            return

        for contentFile in contentFilePaths:
            with open(contentFile, "r") as infile:
                content = json.load(infile)

                # reformat json
                reformatted_dict = {}
                for node in content["nodes"].keys():
                    node_dict = content["nodes"][node]
                    if len(node_dict["character"]) == 0:
                        print(f" |-> CHARACTER CONTENT NOT EXPORTED: ({node_dict})")
                        continue

                    # parse main
                    character_name = GameDB.getWorldName(node_dict.pop("character"))
                    node_dict["drops"] = list(map(GameDB.getWorldName, node_dict["drops"]))
                    node_dict["spells"] = list(map(GameDB.getWorldName, node_dict["spells"]))
                    node_dict["merchandise"] = list(map(GameDB.getWorldName, node_dict["merchandise"]))

                    # add to main dict
                    reformatted_dict[character_name] = node_dict

                # export json
                fileName = os.path.splitext(os.path.basename(contentFile))[0]
                dest = os.path.join(self.paths["db_export_path"], fileName + GameDB.content_ext)
                self._export(reformatted_dict, dest)
                print(f" |-> CHARACTER CONTENT EXPORTED: ({dest})")

    def export_quest_content(self, *questFilePaths) -> None:
        print("--> EXPORTING QUEST CONTENT")

        if len(questFilePaths) == 0:
            print(" |-> ABORTING: NO PATHS GIVEN")
            return

        for questFile in questFilePaths:
            with open(questFile, "r") as infile:
                content = json.load(infile)

                # reformat json
                reformatted_dict = {}
                for node in content["nodes"].keys():

                    # quest needs to have: 
                    # name, at least one objective, and quest giver/completer
                    node_dict = content["nodes"][node]
                    if node_dict["questName"].strip() == "" \
                    or len(node_dict["questGiver"]) == 0 \
                    or len(node_dict["questCompleter"]) == 0 \
                    or len(node_dict["objectives"].keys()) == 0:
                        continue

                    # parse main
                    quest_giver = GameDB.getWorldName(node_dict.pop("questGiver"))
                    node_dict["nextQuest"] = list(map(GameDB.getWorldName, node_dict["nextQuest"]))
                    node_dict["reward"] = list(map(GameDB.getWorldName, node_dict["reward"]))
                    node_dict["questCompleter"] = GameDB.getWorldName(node_dict["questCompleter"])

                    # parse objective
                    objectives = {}
                    for objective in node_dict["objectives"].keys():
                        world_object_name = GameDB.getWorldName(node_dict["objectives"][objective].pop("worldObject"))
                        del node_dict["objectives"][objective]["wildcard"]
                        node_dict["objectives"][objective]["extraContent"]["reward"] = \
                            GameDB.getWorldName(node_dict["objectives"][objective]["extraContent"]["reward"])
                        objectives[world_object_name] = node_dict["objectives"][objective]
                    del node_dict["objectives"]
                    node_dict["objectives"] = objectives

                    # export json
                    reformatted_dict[quest_giver] = node_dict

                # export json
                fileName = os.path.splitext(os.path.basename(questFile))[0]
                dest = os.path.join(self.paths["db_export_path"], fileName + GameDB.content_ext)
                self._export(reformatted_dict, dest)
                print(f" |-> QUEST CONTENT EXPORTED: ({dest})")
                    
