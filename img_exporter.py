#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import os
import csv
import json
import xml.etree.ElementTree as ET


class ImageExporter:

    filename = "ImageDB"
    
    def __init__(self, file_path_data):
        # open and read paths
        self.paths = {"csv_file":"", "export_path":""}
        with open(file_path_data, "r") as f:
            self.paths = json.load(f)
        # open csv and read contents
        self.data = []
        if not os.path.exists(self.paths["csv_file"]):
            print("--> CSV FILE DOESN'T EXIST: (%s)" % self.paths["csv_file"])
            exit(1)
        with open(self.paths["csv_file"], "r") as f:
            csv_reader = csv.reader(f, delimiter=",")
            for row in csv_reader:
                self.data.append(row)
    
    def export_meta(self):
        # make xml
        root = ET.Element(ImageExporter.filename)
        for row in self.data[1:]:
            ET.SubElement(root, "img", {"name": row[0] + ".png", "total":row[1], "moving":row[2], \
                "dying":row[3], "attacking":row[4],"weapon":row[5], "swing":row[6], "body":row[7]})
        # write xml
        dest = os.path.join(self.paths["export_path"], ImageExporter.filename + ".xml")
        tree = ET.ElementTree(root)
        tree.write(dest, encoding="UTF-8", xml_declaration=True)
        print("--> IMAGE DATA EXPORTED")
