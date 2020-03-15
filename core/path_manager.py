#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import json


class PathManager:
    @staticmethod
    def get_master_path():
        return os.path.join(os.path.dirname(__file__), os.pardir, "paths.json")

    @staticmethod
    def get_paths():
        data_paths = {}
        with open(PathManager.get_master_path(), "r") as f:
            data_paths = json.load(f)
            for parent_key in ["game", "tiled"]:
                for key in data_paths[parent_key]:
                    if key != "root":
                        data_paths[parent_key][key] = os.path.join(data_paths[parent_key]["root"],
                            data_paths[parent_key][key])
        return data_paths
