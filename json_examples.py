"""Working with JSONs"""
import json
import arcpy

# Example JSON
person = '{"name": "Joe", "languages": ["Python", "Java"]}'

# Convert it to a Python dictionary
py_person = json.loads(person)
print(py_person["languages"])


# Read a JSON from a file
with open(r'c:\GIS\Data\person.json', 'r') as person:
    py_person = json.load(person)
    print(py_person["languages"])

# Convert to a Python dictionary to a JSON object
person = {
    "name": "Joe",
    "languages": ["Python", "Java"]
    }

json_person = json.dumps(person)
print(json_person)

# Write a JSON object to a file
person = {"name": "Al", "languages": ["Python", "C"]}
with open(r"C:\GIS\Data\newperson.json", "w") as json_file:
    json.dump(person, json_file, indent=4)

# Create a point from a JSON entry
geo = {"x": -124.7548, "y": 46.5783, "spatialReference": {"wkid": 4326}}
point = arcpy.AsShape(geo, True)

# Create a line from a JSON entry
geo = {
    "paths": [
        [[166.4359, 19.5043], [166.4699, 19.5098],
         [166.5086, 19.4887], [166.5097, 19.4669],
         [166.4933, 19.4504], [166.4617, 194410]]],
    "spatialReference": {"wkid": 4326}}

polyline = arcpy.AsShape(geo, True)