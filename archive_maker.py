#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import json
import os.path
import tarfile
from datetime import datetime


class Archiver:
    
    # %s is for the date/time
    archive_name_format = "%s_Tides_of_War"
    archive_ext = ".tar.gz"

    def __init__(self, file_path_data):
        self.files_to_archive = []
        self.backup_dir = ""
        with open(file_path_data, "r") as f:
            data = json.load(f)
            self.files_to_archive = data["archive"]
            self.backup_dir = data["backup_dir"]

    def backup(self):
        # make name for archive file
        tar_name = Archiver.archive_name_format % datetime.now().strftime("%Y-%m-%d_%H") + Archiver.archive_ext
        # make path
        tar_name = os.path.join(self.backup_dir, tar_name)
        # archive files
        with tarfile.open(tar_name, "w:gz") as tar:
            print("--> MAKING BACKUP:")
            for f in self.files_to_archive:
                print(" |-> ADDING: (%s)" % f)
                tar.add(f)
        print("--> BACKUP MADE: (%s)" % tar_name)
