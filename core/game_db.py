#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import enum
import json
import pyexcel_ods
import xml.etree.ElementTree as ET

from core.path_manager import PathManager


class DataBases(enum.Enum):
    IMAGEDB = "Image"
    ITEMDB = "Item"
    QUESTDB = "Quest"
    SPELLDB = "Spell"


class GameDB:

    defined_text_tags = [
        "description", "start", "active", "completed", "delivered",
        "receiver_completed", "receiver_delivered"
    ]
    repeated_tags = {
        DataBases.IMAGEDB: "img",
        DataBases.ITEMDB: "item",
        DataBases.QUESTDB: "quest",
        DataBases.SPELLDB: "spell"
    }
    db_ext = ".ods"

    def __init__(self):
        self.paths = {}
        paths = PathManager.get_paths()
        self.paths["db_dir"] = paths["db_dir"]
        self.paths["db_export_path"] = paths["db_export_path"]
        self.data = {}
        self.load_db()

    def get_database(self, database):
        return self.data[database]["data"]

    def load_db(self):
        for db in os.listdir(self.paths["db_dir"]):
            db_file_name = os.path.splitext(db)[0].upper()
            if db.endswith(GameDB.db_ext) and db_file_name in [
                    d.name for d in DataBases
            ]:
                # load db
                workbook = pyexcel_ods.get_data(
                    os.path.join(self.paths["db_dir"], db))
                sheets = json.loads(json.dumps(workbook))
                # loop through all sheets in file
                for sheet_name in sheets:
                    matrix = sheets[sheet_name]
                    # get all header names
                    headers = []
                    for header in matrix[0]:
                        header = str(header).strip()
                        if header != "":
                            headers.append(header)
                    # clean data
                    rows_to_delete = []
                    for row in range(1, len(matrix)):
                        # resize row
                        header_size = len(headers)
                        row_size = len(matrix[row])
                        if row_size < header_size:
                            # pads row
                            for i in range(header_size - row_size):
                                matrix[row].append("")
                        else:
                            # crops row
                            matrix[row] = matrix[row][:header_size]
                        # normalize all data
                        for column in range(len(matrix[row])):
                            matrix[row][column] = str(
                                matrix[row][column]).strip()
                            # select empty rows to delete
                            if matrix[row][0] == "":
                                rows_to_delete.append(matrix[row])
                                break
                    # delete empty rows
                    for row in rows_to_delete:
                        matrix.remove(row)
                    # matrix -> dict
                    data = {}
                    for row in range(1, len(matrix)):
                        temp = {}
                        for column in range(1, len(matrix[row])):
                            temp[headers[column]] = matrix[row][column]
                        data[matrix[row][0]] = temp
                    # set data
                    self.data[DataBases[db_file_name]] = {
                        "data": data,
                        "tag": GameDB.repeated_tags[DataBases[db_file_name]]
                    }

    def export_databases(self):
        # TODO doesn't work due to new database structure change
        print("--> !!!NOT IMPLEMENTED!!!")
        return
        print("--> EXPORTING DATABASES")
        for sheet in self.data:
            data = self.get_database(sheet)
            sheet_name = sheet.name
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
                    if header in GameDB.defined_text_tags:
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
                element = ET.SubElement(root, self.data[sheet_name]["tag"],
                                        attributes)
                for sub_tag in defined_sub_tags:
                    ET.SubElement(element,
                                  sub_tag).text = defined_sub_tags[sub_tag]
                for objective in objectives:
                    ET.SubElement(element, "objective", {
                        "name": objective,
                        "amount": objectives[objective]
                    })
            # make path
            dest = os.path.join(self.paths["db_export_path"], sheet_name + ".xml")
            # write xml
            tree = ET.ElementTree(root)
            tree.write(dest, encoding="UTF-8", xml_declaration=True)
            print(" |-> DATABASE EXPORTED: (%s)" % sheet_name)
        print("--> ALL DATABASES EXPORTED")
