#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import json


class PathManager:
    @staticmethod
    def get_path_dir():
        return os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.pardir)), "paths")

    @staticmethod
    def get_master_path():
        return os.path.join(PathManager.get_path_dir(), "paths.json")

    @staticmethod
    def get_paths():
        data_paths = {}
        with open(PathManager.get_master_path(), "r") as f:
            data_paths = json.load(f)
            for file_path in data_paths:
                data_paths[file_path] = os.path.join(
                    PathManager.get_path_dir(), data_paths[file_path])
        return data_paths
