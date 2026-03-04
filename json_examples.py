"""Working with JSONs"""
import json

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
