"""Working with XML files."""
from xml.dom import minidom

kml = minidom.parse("example.kml")

placemarks = kml.getElementsByTagName("Placemark")

coords = placemarks[0].getElementsByTagName("coordinates")

point = coords[0].firstChild.data

x,y,z = [float(c) for c in point.split(",")]

print(f"x: {x}, y: {y}, z: {z}")
