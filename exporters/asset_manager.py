#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import re
import os
import json
import shutil
import game_db
import image_editor
import path_manager


class AssetManager:

    img_ext = ".png"

    def __init__(self, file_path_data):
        self.assets = {}
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

    def make_sprite_deaths(self, *order_paths):
        # load img db
        db_path = path_manager.PathManager.get_paths()["db"]
        img_data = game_db.GameDB(db_path).get_database(
            game_db.DataBases.IMAGEDB)
        # determine order
        batch_order = []
        if len(order_paths) == 0:
            batch_order = [
                os.path.join(self.assets["game_character_dir"], f)
                for f in os.listdir(self.assets["game_character_dir"])
            ]
        else:
            batch_order = order_paths
            for order in batch_order:
                if not os.path.isfile(order):
                    print(
                        "--> ERROR: (order_paths) CANNOT CONTAIN DIRECTOR(Y/IES)\n--> ABORTING"
                    )
                    return
        # start command
        command = "gimp -idf"
        # build command
        print("--> MAKING SPRITE DEATH ANIMATIONS")
        for src in batch_order:
            if src.endswith(AssetManager.img_ext):
                # make args
                img_name = os.path.splitext(os.path.basename(src))[0]
                dest = src
                if not img_name in img_data:
                    print(
                        " |-> SPRITE DOESN'T HAVE FRAME DATA, SKIPPING: (%s)" %
                        src)
                    continue
                h_frames = int(img_data[img_name]["total"])
                death_frame_start = h_frames - int(
                    img_data[img_name]["attacking"]) - 4
                # append arg
                command += ' -b \'(python-fu-death-anim-batch RUN-NONINTERACTIVE "%s" "%s" %d %d)\'' % (
                    src, dest, h_frames, death_frame_start)
            elif len(order_paths) != 0:
                print(
                    "--> ERROR: (order_paths) ARG WRONG TYPE, MUST BE ABSOLUTE ADDRESS PNG FILE PATH"
                )
        command += " -b '(gimp-quit 0)'"
        # execute command
        os.system(command)
        print("--> SPRITE DEATH ANIMATIONS MADE")

    def make_sym_links(self):
        syms_made = []
        # file naming convention used
        pattern = re.compile("[0-9]+%s" % AssetManager.img_ext)
        # loop through all dirs to find hard copies and send to the game asset dir
        print("--> MAKING SYM LINKS")
        for dirpath, dirnames, filenames in os.walk(
                self.assets["tiled_character_dir"]):
            for file_name in filenames:
                src = os.path.join(dirpath, file_name)
                if not os.path.islink(src) and re.search(pattern, file_name):
                    dest = os.path.join(self.assets["game_character_dir"],
                                        file_name)
                    shutil.move(src, dest)
                    os.symlink(dest, src)
                    syms_made.append(dest)
                    print(" |-> SYM LINK MADE: (%s) -> (%s)" % (src, dest))
        print("--> ALL SYM LINKS MADE")
        return syms_made
