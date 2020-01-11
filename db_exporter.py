#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import os
import csv
import json
import xml.etree.ElementTree as ET


class DBExporter:

    # key must match csv filename
    name_tag = {"ImageDB":"img", "ItemDB":"item", "SpellDB":"spell"}
    csv_ext = ".csv"
    
    def __init__(self, file_path_data):
        self.paths = {"csv_dir":"", "export_path":""}
        with open(file_path_data, "r") as f:
            self.paths = json.load(f)
        self.data = {}
        self.load_csv()
        
    def load_csv(self):
        os.chdir(self.paths["csv_dir"])
        for csv_file in os.listdir():
            if csv_file.endswith(DBExporter.csv_ext):
                with open(csv_file, "r") as f:
                    csv_data = csv.reader(f, delimiter=",")
                    file_name = os.path.splitext(csv_file)[0]
                    self.data[file_name] = []
                    for row in csv_data:
                        self.data[file_name].append(row)

    def export_databases(self):
        for name, tag in DBExporter.name_tag.items():
            # make xml
            matrix = self.data[name]
            root = ET.Element(name)
            attributes = {}
            description = ""
            for i in range(1, len(matrix)):
                for j in range(len(matrix[0])):
                    if matrix[0][j].strip() == "description":
                        description = matrix[i][j].strip()
                    else:
                        attributes[matrix[0][j].strip()] = matrix[i][j].strip()
                element = ET.SubElement(root, tag, attributes)
                if description != "":
                    ET.SubElement(element, "description").text = description
                    description = ""
            # make path
            dest = os.path.join(self.paths["export_path"], name + ".xml")
            # write xml
            tree = ET.ElementTree(root)
            tree.write(dest, encoding="UTF-8", xml_declaration=True)
            print("--> DATABASE: (%s) EXPORTED" % name)
