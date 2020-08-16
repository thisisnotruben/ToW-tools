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

    db_ext = ".ods"
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

    def _load_db(self):
        self.conn = sqlite3.connect(self.database_path)
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
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def export_databases(self):
        print("--> EXPORTING DATABASES")
        for database in [DataBases.ITEMDB.value, DataBases.SPELLDB.value, DataBases.IMAGEDB.value]:
            # gather
            query = "SELECT * FROM image;" if database == DataBases.IMAGEDB.value \
                else "SELECT * FROM WorldObject natural join %s;" % database
            tuples = self.execute_query(query)
            attribute_names = [attName[0] for attName in self.cursor.description]
            data = {
                t[0]: dict(zip(attribute_names[1:], t[1:]))
                for t in tuples
            }
            # export
            dest = os.path.join(self.paths["db_export_path"], "%s.json" % database)
            with open(dest, "w") as outfile:
                json.dump(data, outfile, indent=4)
                print(" |-> DATABASE EXPORTED: (%s)" % dest)
        print("--> ALL DATABASES EXPORTED")

    def export_character_content(self):
        # util function
        get_world_name = lambda world_packet: world_packet[0] if len(world_packet) > 0 else ""
        # start main function
        print("--> EXPORTING CHARACTER CONTENT")
        for content_file in os.listdir(self.paths["character_content_dir"]):
            if content_file.endswith(GameDB.content_ext):
                # make path and load file
                src = os.path.join(self.paths["character_content_dir"], content_file)
                with open(src, "r") as infile:
                    content = json.load(infile)
                    # reformat json
                    reformatted_dict = {}
                    for node in content["nodes"].keys():
                        node_dict = content["nodes"][node]
                        if len(node_dict["character"]) == 0:
                            print(" |-> CHARACTER CONTENT NOT EXPORTED: (%s)" \
                                % node_dict)
                            continue
                        character_name = get_world_name(node_dict.pop("character"))
                        node_dict["drops"] = list(map(get_world_name, node_dict["drops"]))
                        node_dict["spells"] = list(map(get_world_name, node_dict["spells"]))
                        node_dict["merchandise"] = list(map(get_world_name, node_dict["merchandise"]))
                        # add to main dict
                        reformatted_dict[character_name] = node_dict
                    # export json
                    dest = os.path.join(self.paths["db_export_path"], content_file)
                    with open(dest, "w") as outfile:
                        print(" |-> CHARACTER CONTENT EXPORTED: (%s)" % dest)
                        json.dump(reformatted_dict, outfile, indent=4)
        print("--> ALL CHARACTER CONTENT EXPORTED")

    def export_quest_content(self):
        # util function
        get_world_name = lambda world_packet: world_packet[0] if len(world_packet) > 0 else ""
        # start main function
        print("--> EXPORTING QUEST CONTENT")
        for content_file in os.listdir(self.paths["quest_content_dir"]):
            if content_file.endswith(GameDB.content_ext):
                # make path and load file
                src = os.path.join(self.paths["quest_content_dir"], content_file)
                with open(src, "r") as infile:
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
                        quest_giver = get_world_name(node_dict.pop("quest_giver"))
                        node_dict["next_quest"] = list(map(get_world_name, node_dict["next_quest"]))
                        node_dict["reward"] = list(map(get_world_name, node_dict["reward"]))
                        node_dict["quest_completer"] = get_world_name(node_dict["quest_completer"])
                        # parse objective
                        objectives = {}
                        for objective in node_dict["objectives"].keys():
                            world_object_name = get_world_name(node_dict["objectives"][objective].pop("world_object"))
                            del node_dict["objectives"][objective]["wildcard"]
                            node_dict["objectives"][objective]["extra_content"]["reward"] = \
                                get_world_name(node_dict["objectives"][objective]["extra_content"]["reward"])
                            objectives[world_object_name] = node_dict["objectives"][objective]
                        del node_dict["objectives"]
                        node_dict["objectives"] = objectives
                        # export json
                        reformatted_dict[quest_giver] = node_dict
                    # export json
                    dest = os.path.join(self.paths["db_export_path"], content_file)
                    with open(dest, "w") as outfile:
                        print(" |-> CHARACTER CONTENT EXPORTED: (%s)" % dest)
                        json.dump(reformatted_dict, outfile, indent=4)
        print("--> ALL CHARACTER CONTENT EXPORTED")
                    
