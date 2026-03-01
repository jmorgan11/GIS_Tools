"""Example using Zip files."""
import zipfile
import os

# Read a zip file
print("Reading zip file")
zip = open(r"C:\Temp\Test.zip", "rb")
myzip = zipfile.ZipFile(zip)

# Contents of a zip file
print("\nRead contents of a zip file...")
for file in myzip.namelist():
    print(file)

# Extract contents one-by-one
print("\nExtracting contents one-by-one...")
for file in myzip.namelist():
    out = open(os.path.join(r'C:\Temp\Extracted', file), "wb")
    out.write(myzip.read(file))
    out.close()

# Extract contents all at one time
print("\nExtracting contents all at once...")
myzip.extractall(r'C:\Temp\Extracted2')

# Zip a single file
print("\nZipping a single file...")
zfile = zipfile.ZipFile(r"C:\Temp\Test2.zip", "w")
zfile.write(r"C:\Temp\Extracted\24003C_20260116_metadata.xml")
zfile.close()

# Zip certain files
print("\nZipping certain files...")
os.chdir(r"C:\Temp\Shapefiles")
zfile = zipfile.ZipFile("shapefiles.zip", "w", zipfile.ZIP_DEFLATED)
files = os.listdir(".")

for f in files:
    print(f)
    extensions = ("shp", "dbf", "prj", "shx")
    if f.endswith(extensions):
        zfile.write(f)
zfile.close()

# Zip a whole folder
print("\nZipping a whole folder...")
mydir = r'C:\Temp\Shapefiles'
zfile = zipfile.ZipFile(r"C:\Temp\newzip.zip", "w")
for root, dirs, files in os.walk(mydir):
    for file in files:
        filepath = os.path.join(root, file)
        zfile.write(filepath)
zfile.close()
