#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
Tiled version tested on: 1.3.1
"""

import os
import sys
import json
import shutil
import db_exporter
import image_editor
import xml.etree.ElementTree as ET


class TiledExporter:

    img_ext = ".png"
    map_ext = ".tmx"
    tileset_ext = ".tsx"
    temp_dir = "debugging_temp"
    special_units = ["critter", "aberration"]
    tags_single = ["actorType", "dialogue", "level"]
    tags_multiple = ["quest", "item", "spell"]
    tag_path = "path"
    tag_spawn = "spawnPos"
    all_tags = []
    cell_size = 16

    def __init__(self, file_path_data):
        self.tiled = {"root":"","map_dir":"", "tileset_dir":"", "character_dir":"", \
            "debug_dir":"", "map_file":"", "template_dir":""}
        self.game  = {"root":"","map_dir":"", "tileset_dir":"", "character_dir":""}
        self.debug = {}
        self.tilesets_32 = []
        # load file_paths
        with open(file_path_data, "r") as f:
            data = json.load(f)
            self.tiled = data["tiled"]
            self.game = data["game"]
            self.debug = data["debug"]
            self.tilesets_32 = data["32"]
        # make rel paths abs paths
        for asset_dir in [self.tiled, self.game]:
            for file_name in asset_dir:
                if file_name != "root":
                    asset_dir[file_name] = os.path.join(asset_dir["root"], asset_dir[file_name])
        # parse file name
        self.file_name = os.path.split(self.tiled["map_file"])[-1]
        # add all tags
        TiledExporter.all_tags = TiledExporter.tags_single + TiledExporter.tags_multiple

    @staticmethod
    def _debug_map_move_files(root_dir, dest_dir):
        for tileset in os.listdir(root_dir):
            if tileset.endswith(TiledExporter.img_ext):
                src = os.path.join(root_dir, tileset)
                shutil.copy(src, dest_dir)

    @staticmethod
    def _get_center_pos(pos=(), size=()):
        offset = round(float(TiledExporter.cell_size) / 2.0)
        x = int(round((int(pos[0]) + int(size[0]) / 2.0) / float(TiledExporter.cell_size)) * float(TiledExporter.cell_size))
        x += offset
        y = int(pos[1]) + offset
        return (int(x), int(y))

    @staticmethod
    def _write_xml(tree, dest):
        tree.write(dest, encoding="UTF-8", xml_declaration=True)

    @staticmethod
    def _format_name(unit_meta, unit_atts):
        base_name = ""
        if "name" in unit_atts:
            base_name = unit_atts["name"]
        elif "template" in unit_atts:
            base_name = unit_atts["template"].split("/")[-1].split(".")[0]
        elif bool(unit_meta):
            base_name = unit_meta[unit_atts["id"]]["img"].split("-")[0]
        return "%s-%s" % (unit_atts["id"], base_name)

    def _get_map_character_layer(self):
        root = ET.parse(self.tiled["map_file"]).getroot()
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

    def _get_map_character_tilesets(self):
        root = ET.parse(self.tiled["map_file"]).getroot()
        tilesets = {}
        for child in root:
            if child.tag == "tileset" and "character" in child.attrib["source"]:
                tilesets[int(child.attrib["firstgid"])] = child.attrib["source"]
        return tilesets

    def _get_character_attributes(self):
        master_dict = {}
        tilesets = self._get_map_character_tilesets()
        root = ET.parse(self.tiled["map_file"]).getroot()
        group_index, layer_index = self._get_map_character_layer()
        os.chdir(self.tiled["map_dir"])
        for child in root[group_index][layer_index]:
            unit_attr = child.attrib
            if "player" in unit_attr.values():
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

    def _get_character_names(self, editor_names):
        names = {}
        unit_meta = self._get_character_attributes()
        group_index, layer_index = self._get_map_character_layer()
        root = ET.parse(self.tiled["map_file"]).getroot()
        for child in root[group_index][layer_index]:
            unit_atts = child.attrib
            if editor_names:
                names[unit_atts["id"]] = TiledExporter._format_name(unit_meta, unit_atts)
            elif "name" in unit_atts:
                names[unit_atts["id"]] = unit_atts["name"]
            else:
                names[unit_atts["id"]] = unit_meta[unit_atts["id"]]["name"]
        return names

    def _get_unit_paths(self):
        unit_paths = {}
        unit_spawn_locs = self._get_unit_spawn_locs()
        for child in ET.parse(self.tiled["map_file"]).getroot():
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
                            parse_points = ""
                            points = []
                            for p in path:
                                parse_points += p.attrib["points"]
                            parse_points = parse_points.split(" ")
                            for p in parse_points:
                                p = p.split(",")
                                p = (int(p[0]) + point_origin[0], int(p[1]) + point_origin[1])
                                points.append(p)
                            unit_paths[path.attrib["name"]] = points
        return unit_paths

    def _get_unit_spawn_locs(self):
        spawn_locs = {}
        group_index, layer_index = self._get_map_character_layer()
        for child in ET.parse(self.tiled["map_file"]).getroot()[group_index][layer_index]:
            unit_atts = child.attrib
            if "width" in unit_atts:
                spawn_loc = TiledExporter._get_center_pos((unit_atts["x"], unit_atts["y"]), (unit_atts["width"], unit_atts["height"]))
                spawn_locs[unit_atts["id"]] = spawn_loc
        return spawn_locs

    def is_debugging(self):
        return os.path.exists(os.path.join(self.tiled["map_dir"], TiledExporter.temp_dir))

    def debug_map(self):
        os.chdir(self.tiled["map_dir"])
        debug = True 
        if os.path.exists(TiledExporter.temp_dir):
            TiledExporter._debug_map_move_files(TiledExporter.temp_dir, self.tiled["tileset_dir"])
            shutil.rmtree(TiledExporter.temp_dir)
            debug = False
        else:
            os.mkdir(TiledExporter.temp_dir)
            TiledExporter._debug_map_move_files(self.tiled["tileset_dir"], TiledExporter.temp_dir)
            TiledExporter._debug_map_move_files(self.tiled["debug_dir"], self.tiled["tileset_dir"])
            with open(os.path.join(TiledExporter.temp_dir, "README.txt"), "w") as f:
                f.write("Don't delete folder or contents of folder manually. If you do, you've done messed up.")
        print("--> MAP DEBUG OVERLAY: %s\n--> PRESS (CTRL-T) TO REFRESH IF HASN'T SHOWN" % debug)

    def make_debug_tilesets(self):
        defined_color_names = [c.name for c in image_editor.Color]
        print("--> MAKING DEBUG TILESETS:")
        for tileset in os.listdir(self.tiled["tileset_dir"]):
            if tileset.endswith(TiledExporter.img_ext):
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
                image_editor.ImageEditor.create_overlay(src, dest, image_editor.Color[self.debug[tileset]].value)
                print(" |-> TILESET MADE: (%s)" % dest)
        print("--> ALL DEBUG TILESETS MADE")

    def make_32_tilesets(self):
        print("--> MAKING 32px TILESETS:")
        for tileset in os.listdir(self.tiled["tileset_dir"]):
            if tileset in self.tilesets_32:
                # make paths
                src = os.path.join(self.tiled["tileset_dir"], tileset)
                new_file_name = "%s_32%s" % (os.path.splitext(tileset)[0], TiledExporter.img_ext)
                dest = os.path.join(self.tiled["tileset_dir"], new_file_name)
                # make 32 image
                image_editor.ImageEditor.pad_height(src, dest, 16, 16)
                print(" |-> TILESET MADE: (%s)" % dest)
        print("--> ALL 32px TILESETS MADE")

    def make_sprite_icons(self):
        print("--> MAKING SPRITE ICONS")
        # load img db
        data_paths = {}
        with open(sys.argv[1], "r") as f:
            data_paths = json.load(f)
            for file_path in data_paths:
                if file_path != "root":
                    data_paths[file_path] = os.path.join(data_paths["root"], data_paths[file_path])
        db = db_exporter.DBExporter(data_paths["db"])
        db.load_db()
        img_data = db.data["ImageDB"]["data"]
        # make character icons
        for img in os.listdir(self.game["character_dir"]):
            if img.endswith(TiledExporter.img_ext):
                # make paths
                src = os.path.join(self.game["character_dir"], img)
                dest = os.path.join(self.tiled["character_dir"], img)
                # get hv frames for current sprite
                img_name = os.path.splitext(img)[0]
                character_hv_frames = ()
                for row in range(len(img_data)):
                    if img_name in img_data[row]:
                        character_hv_frames = (int(img_data[row][1]), 1)
                if character_hv_frames == ():
                    print(" |-> SPRITE DOESN'T HAVE FRAME DATA: (%s)" % src)
                else:
                    # write image
                    image_editor.ImageEditor.crop_frame(src, dest, character_hv_frames, (0,0))
        print("--> ALL SPRITE ICONS MADE")

    def export_tilesets(self):
        print("--> EXPORTING TILESETS")
        if os.path.exists(self.game["tileset_dir"]):
            shutil.rmtree(self.game["tileset_dir"])
        shutil.copytree(self.tiled["tileset_dir"], self.game["tileset_dir"])
        for filename in os.listdir(self.tiled["character_dir"]):
            if filename.endswith(TiledExporter.tileset_ext):
                src = os.path.join(self.tiled["character_dir"], filename)
                dest = self.game["character_dir"]
                shutil.copy(src, dest)
                print(" |-> TILESET EXPORTED: (%s)" % dest)
        print("--> ALL TILESETS EXPORTED")

    def export_map(self):
        tree = ET.parse(self.tiled["map_file"])
        root = tree.getroot()
        group_index, layer_index = self._get_map_character_layer()
        editor_names = self._get_character_names(True)
        spawn_locs = self._get_unit_spawn_locs()
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
                                spawn_loc = TiledExporter._get_center_pos((td_atts["x"], td_atts["y"]), tD_size)
                                td.set("x", str(spawn_loc[0]))
                                td.set("y", str(spawn_loc[1]))
                                td.set("name", TiledExporter._format_name({}, td_atts))
        # for lights and graves
        for tag_name in ["light", "grave"]:
            for group in root:
                if group.tag == "group" and group.attrib["name"] == "meta":
                    for layer in group:
                        if layer.tag == "objectgroup" and tag_name in layer.attrib["name"]:
                            for thing in layer:
                                thing.set("name", TiledExporter._format_name({}, thing.attrib))
        # write to map
        dest = os.path.join(self.game["map_dir"], self.file_name)
        TiledExporter._write_xml(tree, dest)
        print("--> MAP: (%s) EXPORTED" % self.file_name)
      
    def export_meta(self):
        root = ET.parse(self.tiled["map_file"]).getroot()
        # get unit attributes
        group_index, layer_index = self._get_map_character_layer()
        unit_attribute_index = 0
        master_dict = {}
        unit_meta = self._get_character_attributes()
        unit_patrol_paths = self._get_unit_paths()
        spawn_locs = self._get_unit_spawn_locs()
        layer = root[group_index][layer_index]
        editor_names = self._get_character_names(True)
        game_names = self._get_character_names(False)
        for unit_index in range(len(layer)):    
            unit_atts = layer[unit_index].attrib
            unit_ID = layer[unit_index].attrib["id"]
            if not "player" in unit_atts.values():
                master_dict[unit_ID] = {
                    "editorName":editor_names[unit_ID],
                    "name":game_names[unit_ID].strip(),
                    "img":os.path.splitext(unit_meta[unit_ID]["img"])[0],
                    "enemy":unit_meta[unit_ID]["enemy"],
                    TiledExporter.tag_spawn: spawn_locs[unit_ID]}
                if unit_ID in unit_patrol_paths:
                    master_dict[unit_ID][TiledExporter.tag_path] = unit_patrol_paths[unit_ID]
                for unit_property in layer[unit_index]:
                    if unit_property.tag == "properties":
                        for unit_attribute in layer[unit_index][unit_attribute_index]:
                            for tag in TiledExporter.all_tags:
                                attribute_name = unit_attribute.attrib["name"]
                                if attribute_name == tag or tag in attribute_name:
                                    master_dict[unit_ID][attribute_name] = unit_attribute.attrib["value"]
                        unit_attribute_index += 1
                    unit_attribute_index = 0
        # clean data
        clean_dict = {}
        for unit_ID in master_dict:
            if "editorName" in master_dict[unit_ID]:
                unit_editor_name = master_dict[unit_ID]["editorName"]
                del master_dict[unit_ID]["editorName"]
                if not (unit_editor_name.split("-")[0] in TiledExporter.special_units and len(master_dict[unit_ID]) == 1):
                    clean_dict[unit_editor_name] = master_dict[unit_ID]
        master_dict = clean_dict
        # make xml file from dict
        file_name = os.path.splitext(self.file_name)[0]
        root = ET.Element(file_name)
        for unit in master_dict:
            unit_root = ET.SubElement(root, "unit", {"name":master_dict[unit]["name"], "editorName": unit, "img":master_dict[unit]["img"], \
                "enemy":master_dict[unit]["enemy"], "x":str(master_dict[unit][TiledExporter.tag_spawn][0]), \
                "y":str(master_dict[unit][TiledExporter.tag_spawn][1])})
            for tag in TiledExporter.tags_single:
                if tag in master_dict[unit]:
                    ET.SubElement(unit_root, tag).text = str(master_dict[unit][tag])
            for attribute_name in TiledExporter.tags_multiple:
                if attribute_name in master_dict[unit]:
                    attr_root = ET.SubElement(unit_root, attribute_name + "s")
                    for attribute in master_dict[unit]:
                        if attribute_name in attribute:
                            ET.SubElement(attr_root, attribute_name, {"name":str(master_dict[unit][attribute])})
            if TiledExporter.tag_path in master_dict[unit]:
                path_root = ET.SubElement(unit_root, TiledExporter.tag_path)
                for point in master_dict[unit][TiledExporter.tag_path]:
                    ET.SubElement(path_root, "point", {"x":str(point[0]),"y":str(point[1])})
        # write xml to dest
        tree = ET.ElementTree(root)
        dest = os.path.join(self.game["meta_dir"], file_name + "DB.xml")
        TiledExporter._write_xml(tree, dest)
        print("--> META: (%s) EXPORTED" % self.file_name)
