#!/usr/bin/env python3

"""
Ruben Alvarez Reyes
"""

import os
import csv
import json
import pyexcel_ods
import xml.etree.ElementTree as ET


class DBExporter:

    defined_text_tags = ["description", "start", "active", "completed", "delivered", "receiver_completed", "receiver_delivered"]
    db_ext = "ods"
    
    def __init__(self, file_path_data):
        self.paths = {"export_path":"", "db_dir":""}
        with open(file_path_data, "r") as f:
            self.paths = json.load(f)
        self.data = {}

    def load_db(self):
        for db in os.listdir(self.paths["db_dir"]):
            if db.endswith(DBExporter.db_ext):
                # load db
                workbook = pyexcel_ods.get_data(os.path.join(self.paths["db_dir"], db))
                sheets = json.loads(json.dumps(workbook))
                # clean data
                for sheet_name in sheets:
                    sheet = sheets[sheet_name]
                    rows_to_delete = []
                    max_row_size = max([len(r) for r in sheet])
                    for row in range(len(sheet)):
                        row_size = len(sheet[row])
                        for column in range(row_size):
                            sheet[row][column] = str(sheet[row][column])
                        if row_size == 0:
                            rows_to_delete.append(sheet[row])
                        elif row_size < max_row_size:
                            for i in range(row_size, max_row_size):
                                sheet[row].append("")
                    for row in rows_to_delete:
                        sheet.remove(row)
                    # set data
                    self.data[sheet_name] = {"data":sheet, "tag":os.path.splitext(db)[0]}

    def export_databases(self):
        self.load_db()
        for sheet_name in self.data:
            # get data
            data = self.data[sheet_name]["data"]
            # make xml
            root = ET.Element(sheet_name)
            for row in range(1, len(data)):
                defined_sub_tags = {}
                attributes = {}
                objectives = {}
                objective_key = ""
                for column in range(len(data[0])):
                    header = data[0][column].strip()
                    value = data[row][column].strip()
                    if header in DBExporter.defined_text_tags:
                        defined_sub_tags[header] = value
                    elif header == "":
                        if value != "":
                            if objective_key == "":
                                objective_key = value
                            elif not value.isnumeric():
                                print("--> ERROR PARSING DATABASE: (%s)" % sheet_name, \
                                    "\n--> OBJECTIVE NOT SET RIGHT IN [ROW][COLUMN]: [%s][%s]" % (row, column))
                                exit(1)
                            else:
                                objectives[objective_key] = value
                                objective_key = ""
                    else:
                        attributes[header] = value
                element = ET.SubElement(root, self.data[sheet_name]["tag"], attributes)
                for sub_tag in defined_sub_tags:
                    ET.SubElement(element, sub_tag).text = defined_sub_tags[sub_tag]
                for objective in objectives:
                    ET.SubElement(element, "objective", {"name":objective, "amount":objectives[objective]})
            # make path
            dest = os.path.join(self.paths["export_path"], sheet_name + ".xml")
            # write xml
            tree = ET.ElementTree(root)
            tree.write(dest, encoding="UTF-8", xml_declaration=True)
            print("--> DATABASE: (%s) EXPORTED" % sheet_name)
