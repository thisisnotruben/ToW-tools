#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
Tiled version tested on: 1.3.1
"""

import os
import json
import shutil
import xml.etree.ElementTree as ET
from distutils.util import strtobool

from core.game_db import GameDB, DataBases
from core.image_editor import ImageEditor, Color
from core.path_manager import PathManager


class Tiled:

    img_ext: str = ".png"
    map_ext: str = ".tmx"
    tileset_ext = ".tsx"
    temp_dir: str = "debugging_temp"
    special_units: list = ["critter", "aberration"]
    tag_path: str = "path"
    tag_spawn: str = "spawnPos"
    tagTypes: dict = {"name": str, "enemy":bool, "level":int}
    cell_size: int = 16

    def __init__(self):
        self.tiled: dict = dict()
        self.game: dict = dict()
        self.debug: dict = dict()
        self.tilesets_32: list = []
        data = PathManager.get_paths()
        self.tiled = data["tiled"]
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
    def _formatName(unitMeta, unitAtts: dict) -> str:
        baseName: str = ""
        if "name" in unitAtts:
            baseName = unitAtts["name"]
        elif "template" in unitAtts:
            baseName = unitAtts["template"].split("/")[-1].split(".")[0]
        elif bool(unitMeta):
            baseName = unitMeta[unitAtts["id"]]["img"].split("-")[0]
        return "%s-%s" % (unitAtts["id"], baseName)

    def _getMapCharacterLayer(self, root) -> tuple:
        group_index: int = 0
        layer_index: int = 0
        for child in root:
            if child.tag == "group" and child.attrib["name"] == "zed":
                for child in root[group_index]:
                    if child.tag == "objectgroup" and child.attrib["name"] == "characters":
                        break
                    layer_index += 1
                break
            group_index += 1
        return (group_index, layer_index)

    def _getMapCharacterTilesets(self, root) -> dict:
        tilesets: dict = dict()
        for group in root:
            if group.tag == "tileset" and "character" in group.attrib["source"]:
                tilesets[int(group.attrib["firstgid"])] = group.attrib["source"]
        return tilesets

    def _getCharacterAttributes(self, root) -> dict:
        masterDict: dict = dict()
        tilesets: dict = self._getMapCharacterTilesets(root)
        group_index, layer_index = self._getMapCharacterLayer(root)

        os.chdir(self.tiled["map_dir"])

        for child in root[group_index][layer_index]:
            unitAttr: dict = child.attrib

            if "template" in unitAttr:
                continue

            characterID: int = int(unitAttr["gid"])
            characterTilesetID: int = -1
            for tilesetID in tilesets:
                if characterID >= tilesetID:
                    characterTilesetID = tilesetID

            characterAttr: dict = dict()
            # set default attributes from tileset
            i: int = 0
            characterTilesetRoot = ET.parse(tilesets[characterTilesetID]).getroot()
            for group in characterTilesetRoot:
                if "id" in group.attrib and int(group.attrib["id"]) == characterID - characterTilesetID:
                    for attribute in characterTilesetRoot[i]:

                        if attribute.tag == "properties":
                            for attrib in attribute:
                                attrib = attrib.attrib
                                characterAttr[attrib["name"]] = attrib["value"]
                        elif attribute.tag == "image":
                            tex_name = attribute.attrib["source"]
                            characterAttr["img"] = tex_name
                i += 1

            # set map character attributes if set
            for characterProperties in child:
                if characterProperties.tag == "properties":
                    for characterProperty in characterProperties:
                        attributes: dict = characterProperty.attrib
                        characterAttr[attributes["name"]] = attributes["value"]

            masterDict[unitAttr["id"]] = characterAttr
        return masterDict

    def _getCharacterNames(self, editorNames: bool, root) -> dict:
        names: dict = dict()
        unitMeta: dict = self._getCharacterAttributes(root)
        groupIndex, layerIndex = self._getMapCharacterLayer(root)

        name: str = ""
        for child in root[groupIndex][layerIndex]:
            attributes: dict = child.attrib

            if editorNames:
                name = Tiled._formatName(unitMeta, attributes)
            elif "name" in attributes:
                name = attributes["name"]
            elif "template" not in attributes:
                name = unitMeta[attributes["id"]]["name"]
            names[attributes["id"]] = name

        return names

    def _getUnitPaths(self, root) -> dict:
        unit_paths: dict = dict()
        unit_spawn_locs = self._getUnitSpawnLocs(root)
        for child in root:
            if child.tag == "group" and child.attrib["name"] == "meta":
                for sub_child in child:
                    if sub_child.tag == "objectgroup" and sub_child.attrib["name"] == "paths":
                        for path in sub_child:
                            if not "name" in path.attrib or not path.attrib["name"].isnumeric():
                                print("--> NO NAME SET IN PATH-ID: %s\n--> NAME NEEDS TO BE UNIT-ID\n--> ABORTING" % path.attrib["id"])
                                exit(1)
                            elif not path.attrib["name"] in unit_spawn_locs:
                                print("--> PATH NAME: %s DOESN'T MATCH WITH ANY CHARACTER-ID\n--> ABORTING" % path.attrib["name"])
                                exit(1)
                            point_origin = unit_spawn_locs[path.attrib["name"]]
                            parse_points: str = ""
                            points: list = []
                            for p in path:
                                parse_points += p.attrib["points"]
                            parse_points = parse_points.split(" ")
                            for p in parse_points:
                                p = p.split(",")
                                p = (int(p[0]) + point_origin[0], int(p[1]) + point_origin[1])
                                points.append(p)
                            unit_paths[path.attrib["name"]] = points
        return unit_paths

    def _getUnitSpawnLocs(self, root) -> dict:
        spawnPos: dict = dict()
        group_index, layer_index = self._getMapCharacterLayer(root)
        for child in root[group_index][layer_index]:
            unitAtts: dict = child.attrib

            if "width" in unitAtts:
                spawn_loc: tuple = Tiled._getCenterPos((unitAtts["x"], unitAtts["y"]), (unitAtts["width"], unitAtts["height"]))
                spawnPos[unitAtts["id"]] = spawn_loc

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
        print("--> MAP DEBUG OVERLAY: %s\n--> PRESS (CTRL-T) TO REFRESH IF HASN'T SHOWN" % debug)

    def make_debug_tilesets(self):
        defined_color_names = [c.name for c in Color]
        print("--> MAKING DEBUG TILESETS:")
        for tileset in os.listdir(self.tiled["tileset_dir"]):
            if tileset.endswith(Tiled.img_ext):
                # check if color is defined
                if not self.debug[tileset] in defined_color_names:
                    print("--> COLOR: (%s) NOT DEFINED FOR TILESET: (%s)\n--> DEFINED COLORS:" % (self.debug[tileset], tileset))
                    for color in defined_color_names:
                        print(" |-> ", color)
                    print("--> ABORTING")
                    exit(1)
                # make paths
                src = os.path.join(self.tiled["tileset_dir"], tileset)
                dest = os.path.join(self.tiled["debug_dir"], tileset)
                # create overlay
                ImageEditor.create_overlay(src, dest, Color[self.debug[tileset]].value)
                print(" |-> TILESET MADE: (%s)" % dest)
        print("--> ALL DEBUG TILESETS MADE")

    def make_32_tilesets(self):
        print("--> MAKING 32px TILESETS:")
        for tileset in os.listdir(self.tiled["tileset_dir"]):
            if tileset in self.tilesets_32:
                # make paths
                new_file_name: str = "%s_32%s" % (os.path.splitext(tileset)[0], Tiled.img_ext)
                src: str = os.path.join(self.tiled["tileset_dir"], tileset)
                dest: str = os.path.join(self.tiled["tileset_dir"], new_file_name)
                # make 32 image
                ImageEditor.pad_height(src, dest, 16, 16)

                print(" |-> TILESET MADE: (%s)" % dest)
        print("--> ALL 32px TILESETS MADE")

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
                    print("--> ERROR: (sprite_paths) CANNOT CONTAIN DIRECTOR(Y/IES)\n--> ABORTING")
                    return
        print("--> MAKING SPRITE ICONS")
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
        print("--> ALL SPRITE ICONS MADE")

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

        groupIndex, layerIndex = self._getMapCharacterLayer(root)
        layer = root[groupIndex][layerIndex]

        for unitIndex in range(len(layer)):
            if "template" in layer[unitIndex].attrib:
                continue

            unitID: str = layer[unitIndex].attrib["id"]
            masterDict[unitID] = {
                "editorName": editorNames[unitID],
                "name": gameNames[unitID].strip(),
                "img": os.path.splitext(unitMeta[unitID]["img"])[0],
                "enemy": bool(strtobool(unitMeta[unitID]["enemy"])),
                "level": int(unitMeta[unitID]["level"]),
                Tiled.tag_path: unitPatrolPaths[unitID] if unitID in unitPatrolPaths else [],
                Tiled.tag_spawn: spawnPos[unitID]
            }

        return masterDict

    def export_tilesets(self):
        print("--> EXPORTING TILESETS")

        if os.path.exists(self.game["tileset_dir"]):
            shutil.rmtree(self.game["tileset_dir"])
        shutil.copytree(self.tiled["tileset_dir"], self.game["tileset_dir"])

        print(" |-> DIRECTORY EXPORTED: (%s)" % self.game["tileset_dir"])

        for filename in os.listdir(self.tiled["character_dir"]):
            if filename.endswith(Tiled.tileset_ext):

                src = os.path.join(self.tiled["character_dir"], filename)
                dest = os.path.join(self.game["character_dir"], filename)
                shutil.copy(src, dest)

                print(" |-> TILESET EXPORTED: (%s)" % dest)

        print("--> ALL TILESETS EXPORTED")

    def _export_map(self):
        tree = ET.parse(self.tiled["map_file"])
        root = tree.getroot()
        group_index, layer_index = self._getMapCharacterLayer(root)
        editor_names = self._getCharacterNames(True, root)
        spawn_locs = self._getUnitSpawnLocs(root)

        # for characters
        for unit in root[group_index][layer_index]:
            unit_id = unit.attrib["id"]
            unit.set("name", str(editor_names[unit_id]))
            if "width" in unit.attrib:
                unit.set("x", str(spawn_locs[unit_id][0]))
                unit.set("y", str(spawn_locs[unit_id][1]))

        # for target_dummys
        tD_size = ()
        for template in os.listdir(self.tiled["template_dir"]):
            if "target_dummy" in template:
                tD_root = ET.parse(os.path.join(self.tiled["template_dir"], template)).getroot()
                for child in tD_root:
                    if child.tag == "object":
                        tD_size = (int(child.attrib["width"]), int(child.attrib["height"]))
        if bool(tD_size):
            for group in root:
                if group.tag == "group" and group.attrib["name"] == "zed":
                    for layer in group:
                        if layer.tag == "objectgroup" and layer.attrib["name"] == "target_dummys":
                            for td in layer:
                                td_atts = td.attrib
                                spawn_loc = Tiled._getCenterPos((td_atts["x"], td_atts["y"]), tD_size)
                                td.set("x", str(spawn_loc[0]))
                                td.set("y", str(spawn_loc[1]))
                                td.set("name", Tiled._formatName({}, td_atts))

        # for lights and graves
        for tag_name in ["light", "grave"]:
            for group in root:
                if group.tag == "group" and group.attrib["name"] == "meta":
                    for layer in group:
                        if layer.tag == "objectgroup" and tag_name in layer.attrib["name"]:
                            for thing in layer:
                                thing.set("name", Tiled._formatName({}, thing.attrib))

        self._removeCharacterTilsets(root)

        # write to map
        dest = os.path.join(self.game["map_dir"], self.file_name + Tiled.map_ext)
        Tiled._writeXml(tree, dest)
        print("--> MAP: (%s) EXPORTED -> (%s)" % (self.file_name, dest))

    def _export_meta(self):
        master_dict = self._getCharacterMapData()
        # reformat data
        clean_dict = {}
        for unit_ID in master_dict:
            if "editorName" in master_dict[unit_ID]:

                unit_editor_name : str = master_dict[unit_ID]["editorName"]
                del master_dict[unit_ID]["editorName"]
                if not (unit_editor_name.split("-")[0] in Tiled.special_units and len(master_dict[unit_ID]) == 1):
                    clean_dict[unit_editor_name] = master_dict[unit_ID]

        master_dict = clean_dict
        # write json
        filename = os.path.splitext(self.file_name)[0]
        dest = os.path.join(self.game["meta_dir"], filename, "%s.json" % filename)
        with open(dest, "w") as outfile:
            json.dump(master_dict, outfile, indent="\t")
        print("--> META: (%s) EXPORTED" % self.file_name)

    def export_all_maps(self, *map_paths):
        if len(map_paths) == 0:
            # if no args, then export all maps
            map_paths = [
                os.path.join(self.tiled["map_dir"], map_file)
                for map_file in os.listdir(self.tiled["map_dir"])
                if map_file.endswith(Tiled.map_ext)
            ]
        for map_file in map_paths:
            self.tiled["map_file"] = map_file
            self.file_name = os.path.splitext(os.path.basename(map_file))[0]
            # export
            self._export_map()
            self._export_meta()

    def _removeCharacterTilsets(self, root) -> None:
        tilesetsToDelete: list = []
        for group in root:
            if group.tag == "tileset" and "character" in group.attrib["source"]:
                tilesetsToDelete.append(group)

        for tileset in tilesetsToDelete:
            root.remove(tileset)

