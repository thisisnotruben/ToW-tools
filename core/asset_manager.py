#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import re
import os
import shutil

from core.game_db import GameDB, DataBases
from core.image_editor import Color, Font, ImageEditor
from core.path_manager import PathManager


class AssetManager:

    img_ext = ".png"

    def __init__(self):
        self.assets = {}
        # load paths
        assets = PathManager.get_paths()
        self.assets["icon_atlas_data"] = assets["icon_atlas_data"]
        self.assets["game_character_dir"] = assets["game"]["character_dir"]
        self.assets["dev_character_dir"] = assets["dev_character_dir"]

    def make_icon_atlas(self):
        icon = self.assets["icon_atlas_data"]
        # check data integrity
        defined_color_names = [c.name for c in Color]
        for color in [icon["bg"], icon["grid"], icon["text"]]:
            if not color in defined_color_names:
                print(
                    "--> COLOR: (%s) NOT DEFINED FOR ICON ATLAS\n--> DEFINED COLORS:"
                    % color)
                for color in defined_color_names:
                    print(" |-> ", color)
                print("--> ABORTING")
                exit(1)
        defined_font_names = [f.name for f in Font]
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
        ImageEditor.resize_image(src, dest, size)
        print(" |-> IMAGE RESIZED")
        ImageEditor.fill_bg(dest, dest,
                                         Color[icon["bg"]].value)
        print(" |-> IMAGE FILLED")
        ImageEditor.line_grid(
            dest, dest, hv_frames, Color[icon["grid"]].value)
        print(" |-> IMAGE GRID LINES MADE")
        ImageEditor.text_grid(
            dest, dest, hv_frames, Color[icon["text"]].value,
            Font[icon["font"]].value)
        print(" |-> IMAGE ENUMERATED")
        print("--> ICON ATLAS MADE: (%s)" % dest)

    def make_sprite_deaths(self, *order_paths):
        # load img db
        img_data = GameDB().get_database(DataBases.IMAGEDB)
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
                self.assets["dev_character_dir"]):
            for file_name in filenames:
                src = os.path.join(dirpath, file_name)
                if not os.path.islink(src) and re.search(pattern, file_name):
                    dest = os.path.join(self.assets["dev_character_dir"],
                                        file_name)
                    shutil.move(src, dest)
                    os.symlink(dest, src)
                    syms_made.append(dest)
                    print(" |-> SYM LINK MADE: (%s) -> (%s)" % (src, dest))
        print("--> ALL SYM LINKS MADE")
        return syms_made
