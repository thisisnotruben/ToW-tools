#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import json
import game_db
import image_editor
import path_manager


class AssetManager:

    img_ext = ".png"

    def __init__(self, file_path_data):
        self.assets = {"icon": {}, "character_dir": ""}
        # load paths
        with open(file_path_data, "r") as f:
            self.assets = json.load(f)

    def make_icon_atlas(self):
        icon = self.assets["icon"]
        # check data integrity
        defined_color_names = [c.name for c in image_editor.Color]
        for color in [icon["bg"], icon["grid"], icon["text"]]:
            if not color in defined_color_names:
                print(
                    "--> COLOR: (%s) NOT DEFINED FOR ICON ATLAS\n--> DEFINED COLORS:"
                    % color)
                for color in defined_color_names:
                    print(" |-> ", color)
                print("--> ABORTING")
                exit(1)
        defined_font_names = [f.name for f in image_editor.Font]
        if not icon["font"] in defined_font_names:
            print(
                "--> FONT: (%s) NOT DEFINED FOR ICON ATLAS\n--> DEFINED FONTS:"
                % icon["font"])
            for font in defined_font_names:
                print(" |-> ", font)
            print("--> ABORTING")
            exit(1)
        # make paths
        src = icon["path"]
        dest = os.path.join(os.path.dirname(icon["path"]), icon["atlas_name"])
        # make atlas attributes
        size = (int(icon["size"][0]), int(icon["size"][1]))
        hv_frames = (int(icon["hv_frames"][0]), int(icon["hv_frames"][1]))
        # make atlas
        print("--> MAKING ICON ATLAS:")
        image_editor.ImageEditor.resize_image(src, dest, size)
        print(" |-> IMAGE RESIZED")
        image_editor.ImageEditor.fill_bg(dest, dest,
                                         image_editor.Color[icon["bg"]].value)
        print(" |-> IMAGE FILLED")
        image_editor.ImageEditor.line_grid(
            dest, dest, hv_frames, image_editor.Color[icon["grid"]].value)
        print(" |-> IMAGE GRID LINES MADE")
        image_editor.ImageEditor.text_grid(
            dest, dest, hv_frames, image_editor.Color[icon["text"]].value,
            image_editor.Font[icon["font"]].value)
        print(" |-> IMAGE ENUMERATED")
        print("--> ICON ATLAS MADE: (%s)" % dest)

    def make_sprite_deaths(self):
        # load img db
        db_path = path_manager.PathManager.get_paths()["db"]
        img_data = game_db.GameDB(db_path).get_database(
            game_db.DataBases.IMAGEDB)
        # start command
        command = "gimp -idf"
        # build command
        print("--> MAKING SPRITE DEATH ANIMATIONS")
        for img in os.listdir(self.assets["character_dir"]):
            if img.endswith(AssetManager.img_ext):
                # make args
                img_name = os.path.splitext(img)[0]
                src = os.path.join(self.assets["character_dir"], img)
                dest = src
                if not img_name in img_data:
                    print(" |-> SPRITE DOESN'T HAVE FRAME DATA: (%s)" % src)
                    continue
                h_frames = int(img_data[img_name]["total"])
                death_frame_start = h_frames - int(
                    img_data[img_name]["attacking"]) - 4
                # append arg
                command += ' -b \'(python-fu-death-anim RUN-NONINTERACTIVE "%s" "%s" %d %d)\'' % (
                    src, dest, h_frames, death_frame_start)
        command += " -b '(gimp-quit 0)'"
        # execute command
        os.system(command)
        print("--> SPRITE DEATH ANIMATIONS MADE")
