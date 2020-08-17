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

    def export_databases(self) -> None:
        print("--> EXPORTING DATABASES")
        for database in [DataBases.ITEMDB.value, DataBases.SPELLDB.value, DataBases.IMAGEDB.value]:
            # gather
            query = "SELECT * FROM image;" if database == DataBases.IMAGEDB.value \
                else f"SELECT * FROM WorldObject natural join {database};"
            tuples = self.execute_query(query)
            attribute_names = [attName[0] for attName in self.cursor.description]
            # image only database data cleanup
            if database == DataBases.IMAGEDB.value:
                attribute_names = list(map(
                    lambda attName: attName.replace("Frames", ""),
                    attribute_names))
                # sqlite doesn't support bool
                meleeIdx = attribute_names.index("melee")
                for i in range(len(tuples)):
                    tuples[i] = list(tuples[i])
                    tuples[i][meleeIdx] = tuples[i][meleeIdx] == 1
            elif database == DataBases.SPELLDB.value:
                # sqlite doesn't support bool
                idxs = [
                    attribute_names.index("ignoreArmor"),
                    attribute_names.index("effectOnTarget"),
                    attribute_names.index("requiresTarget")
                ]
                for i in range(len(tuples)):
                    tuples[i] = list(tuples[i])
                    for j in range(len(idxs)):
                        tuples[i][idxs[j]] = tuples[i][idxs[j]] == 1
            data = {
                t[0]: dict(zip(attribute_names[1:], t[1:]))
                for t in tuples
            }
            # export
            dest = os.path.join(self.paths["db_export_path"], database + GameDB.content_ext)
            with open(dest, "w") as outfile:
                json.dump(data, outfile, indent=4)
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
                with open(dest, "w") as outfile:
                    json.dump(reformatted_dict, outfile, indent=4)
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
                    if node_dict["quest_name"].strip() == "" \
                    or len(node_dict["quest_giver"]) == 0 \
                    or len(node_dict["quest_completer"]) == 0 \
                    or len(node_dict["objectives"].keys()) == 0:
                        continue

                    # parse main
                    quest_giver = GameDB.getWorldName(node_dict.pop("quest_giver"))
                    node_dict["next_quest"] = list(map(GameDB.getWorldName, node_dict["next_quest"]))
                    node_dict["reward"] = list(map(GameDB.getWorldName, node_dict["reward"]))
                    node_dict["quest_completer"] = GameDB.getWorldName(node_dict["quest_completer"])

                    # parse objective
                    objectives = {}
                    for objective in node_dict["objectives"].keys():
                        world_object_name = GameDB.getWorldName(node_dict["objectives"][objective].pop("world_object"))
                        del node_dict["objectives"][objective]["wildcard"]
                        node_dict["objectives"][objective]["extra_content"]["reward"] = \
                            GameDB.getWorldName(node_dict["objectives"][objective]["extra_content"]["reward"])
                        objectives[world_object_name] = node_dict["objectives"][objective]
                    del node_dict["objectives"]
                    node_dict["objectives"] = objectives

                    # export json
                    reformatted_dict[quest_giver] = node_dict

                # export json
                fileName = os.path.splitext(os.path.basename(questFile))[0]
                dest = os.path.join(self.paths["db_export_path"], fileName + GameDB.content_ext)
                with open(dest, "w") as outfile:
                    json.dump(reformatted_dict, outfile, indent=4)
                    print(f" |-> QUEST CONTENT EXPORTED: ({dest})")
                    
