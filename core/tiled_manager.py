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

    img_ext = ".png"
    map_ext = ".tmx"
    tileset_ext = ".tsx"
    temp_dir = "debugging_temp"
    special_units = ["critter", "aberration"]
    tag_path = "path"
    tag_spawn = "spawnPos"
    tagTypes = {"name": str, "enemy":bool, "level":int}
    cell_size = 16

    def __init__(self):
        self.tiled = {}
        self.game = {}
        self.debug = {}
        self.tilesets_32 = []
        data = PathManager.get_paths()
        self.tiled = data["tiled"]
        self.game = data["game"]
        self.debug = data["debug"]
        self.tilesets_32 = data["32"]

    @staticmethod
    def _debug_map_move_files(root_dir, dest_dir):
        for tileset in os.listdir(root_dir):
            if tileset.endswith(Tiled.img_ext):
                src = os.path.join(root_dir, tileset)
                shutil.copy(src, dest_dir)

    @staticmethod
    def _get_center_pos(pos=(), size=()):
        offset = round(float(Tiled.cell_size) / 2.0)
        x = int(round((int(pos[0]) + int(size[0]) / 2.0) / float(Tiled.cell_size)) * float(Tiled.cell_size))
        x += offset
        y = int(pos[1]) + offset
        return (int(x), int(y))

    @staticmethod
    def _write_xml(tree, dest):
        tree.write(dest, encoding="UTF-8", xml_declaration=True)

    @staticmethod
    def _format_name(unit_meta, unit_atts) -> str:
        base_name = ""
        if "name" in unit_atts:
            base_name = unit_atts["name"]
        elif "template" in unit_atts:
            base_name = unit_atts["template"].split("/")[-1].split(".")[0]
        elif bool(unit_meta):
            base_name = unit_meta[unit_atts["id"]]["img"].split("-")[0]
        return "%s-%s" % (unit_atts["id"], base_name)

    def _get_map_character_layer(self, root):
        group_index = 0
        layer_index = 0
        for child in root:
            if child.tag == "group" and child.attrib["name"] == "zed":
                for child in root[group_index]:
                    if child.tag == "objectgroup" and child.attrib["name"] == "characters":
                        break
                    layer_index += 1
                break
            group_index += 1
        return (group_index, layer_index)

    def _get_map_character_tilesets(self, root) -> dict:
        tilesets = {}
        for group in root:
            if group.tag == "tileset" and "character" in group.attrib["source"]:
                tilesets[int(group.attrib["firstgid"])] = group.attrib["source"]
        return tilesets

    def _get_character_attributes(self, root) -> {}:
        master_dict = {}
        tilesets = self._get_map_character_tilesets(root)
        group_index, layer_index = self._get_map_character_layer(root)
        os.chdir(self.tiled["map_dir"])
        for child in root[group_index][layer_index]:
            unit_attr = child.attrib
            if "template" in unit_attr:
                continue
            ID = int(unit_attr["gid"])
            tile_id = -1
            for tileset_id in tilesets:
                if ID >= tileset_id:
                    tile_id = tileset_id
            root = ET.parse(tilesets[tile_id]).getroot()
            master_dict[unit_attr["id"]] = {}
            id_idx = 0
            for child in root:
                if "id" in child.attrib and int(child.attrib["id"]) == ID - tile_id:
                    for attribute in root[id_idx]:
                        if attribute.tag == "properties":
                            for attrib in attribute:
                                attrib = attrib.attrib
                                master_dict[unit_attr["id"]][attrib["name"]] = attrib["value"]
                        elif attribute.tag == "image":
                            tex_name = attribute.attrib["source"]
                            master_dict[unit_attr["id"]]["img"] = tex_name
                id_idx += 1
        return master_dict

    def _get_character_names(self, editor_names: bool, root) -> {}:
        names = {}
        unit_meta = self._get_character_attributes(root)
        group_index, layer_index = self._get_map_character_layer(root)
        for child in root[group_index][layer_index]:
            unit_atts = child.attrib
            if editor_names:
                names[unit_atts["id"]] = Tiled._format_name(unit_meta, unit_atts)
            elif "name" in unit_atts:
                names[unit_atts["id"]] = unit_atts["name"]
            elif "template" not in unit_atts:
                names[unit_atts["id"]] = unit_meta[unit_atts["id"]]["name"]
        return names

    def _get_unit_paths(self, root):
        unit_paths = {}
        unit_spawn_locs = self._get_unit_spawn_locs(root)
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

    def _get_unit_spawn_locs(self, root):
        spawn_locs = {}
        group_index, layer_index = self._get_map_character_layer(root)
        for child in root[group_index][layer_index]:
            unit_atts = child.attrib
            if "width" in unit_atts:
                spawn_loc = Tiled._get_center_pos((unit_atts["x"], unit_atts["y"]), (unit_atts["width"], unit_atts["height"]))
                spawn_locs[unit_atts["id"]] = spawn_loc
        return spawn_locs

    def is_debugging(self):
        return os.path.exists(os.path.join(self.tiled["map_dir"], Tiled.temp_dir))

    def debug_map(self):
        os.chdir(self.tiled["map_dir"])
        debug = True
        if os.path.exists(Tiled.temp_dir):
            Tiled._debug_map_move_files(Tiled.temp_dir, self.tiled["tileset_dir"])
            shutil.rmtree(Tiled.temp_dir)
            debug = False
        else:
            os.mkdir(Tiled.temp_dir)
            Tiled._debug_map_move_files(self.tiled["tileset_dir"], Tiled.temp_dir)
            Tiled._debug_map_move_files(self.tiled["debug_dir"], self.tiled["tileset_dir"])
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
        master_list = []
        for map_file in os.listdir(self.tiled["map_dir"]):
            if map_file.endswith(Tiled.map_ext):
                # extract file paths
                self.tiled["map_file"] = os.path.join(self.tiled["map_dir"], map_file)
                self.file_name = os.path.splitext(map_file)[0]
                # get character data
                unit_data = self._get_character_map_data()
                for unit_id in unit_data:
                    master_list.append({
                        "img": os.path.join(self.tiled["character_dir"], unit_data[unit_id]["img"] + Tiled.img_ext),
                        "map": os.path.splitext(os.path.basename(self.tiled["map_file"]))[0],
                        "race": unit_data[unit_id]["img"].split("-")[0],
                        "editorName": unit_data[unit_id]["editorName"]
                    })
        return master_list

    def _get_character_map_data(self):
        master_dict = {}
        root = ET.parse(self.tiled["map_file"]).getroot()
        # get unit attributes
        group_index, layer_index = self._get_map_character_layer(root)
        unit_attribute_index = 0
        unit_meta = self._get_character_attributes(root)
        unit_patrol_paths = self._get_unit_paths(root)
        spawn_locs = self._get_unit_spawn_locs(root)
        layer = root[group_index][layer_index]
        editor_names = self._get_character_names(True, root)
        game_names = self._get_character_names(False, root)

        for unit_index in range(len(layer)):
            unit_atts = layer[unit_index].attrib
            unit_ID = layer[unit_index].attrib["id"]
            if not "template" in unit_atts:

                master_dict[unit_ID] = {
                    "editorName": editor_names[unit_ID],
                    "name": game_names[unit_ID].strip(),
                    "img": os.path.splitext(unit_meta[unit_ID]["img"])[0],
                    "enemy": bool(strtobool(unit_meta[unit_ID]["enemy"])),
                    "level": int(unit_meta[unit_ID]["level"]),
                    Tiled.tag_path: [],
                    Tiled.tag_spawn: spawn_locs[unit_ID]
                }

                if unit_ID in unit_patrol_paths:
                    master_dict[unit_ID][
                        Tiled.tag_path] = unit_patrol_paths[unit_ID]

                for unit_property in layer[unit_index]:
                    if unit_property.tag == "properties":
                        for unit_attribute in layer[unit_index][unit_attribute_index]:

                            for tag in Tiled.tagTypes.keys():
                                attribute_name = unit_attribute.attrib["name"]
                                if attribute_name == tag:

                                    # don't want to replace custom name is default name
                                    if tag == "name" and master_dict[unit_ID]["name"].strip() != "":
                                        continue
                                    # parse tag to appropriate data type
                                    master_dict[unit_ID][attribute_name] = Tiled.tagTypes[tag](unit_attribute.attrib["value"])

                        unit_attribute_index += 1
                    unit_attribute_index = 0
        return master_dict

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
        group_index, layer_index = self._get_map_character_layer(root)
        editor_names = self._get_character_names(True, root)
        spawn_locs = self._get_unit_spawn_locs(root)

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
                                spawn_loc = Tiled._get_center_pos((td_atts["x"], td_atts["y"]), tD_size)
                                td.set("x", str(spawn_loc[0]))
                                td.set("y", str(spawn_loc[1]))
                                td.set("name", Tiled._format_name({}, td_atts))

        # for lights and graves
        for tag_name in ["light", "grave"]:
            for group in root:
                if group.tag == "group" and group.attrib["name"] == "meta":
                    for layer in group:
                        if layer.tag == "objectgroup" and tag_name in layer.attrib["name"]:
                            for thing in layer:
                                thing.set("name", Tiled._format_name({}, thing.attrib))

        self._removeCharacterTilsets(root)

        # write to map
        dest = os.path.join(self.game["map_dir"], self.file_name + Tiled.map_ext)
        Tiled._write_xml(tree, dest)
        print("--> MAP: (%s) EXPORTED -> (%s)" % (self.file_name, dest))

    def _export_meta(self):
        master_dict = self._get_character_map_data()
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

