#!/usr/bin/env python3

import os
import json


class PathManager:
	@staticmethod
	def get_master_path():
		return os.path.join(os.path.dirname(__file__), os.pardir, "settings.json")

	@staticmethod
	def get_paths():
		data_paths = {}
		with open(PathManager.get_master_path(), "r") as f:
			data = json.load(f)
			for parent_key in ["game", "tiled"]:
				for key in data[parent_key]:
					if key != "root":
						data[parent_key][key] = os.path.join(data[parent_key]["root"],
							data[parent_key][key])
			data_paths = data
		return data_paths
