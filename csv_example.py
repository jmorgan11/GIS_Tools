<<<<<<< Updated upstream
#---------------------------------------------------------------------------------------
# Name:        csv_example.py
# Purpose:     Examples of using CSV files
#
# Author:      Jesse Morgan
#
# Created:     03/02/2026
#---------------------------------------------------------------------------------------
import csv
import fileinput
import arcpy

def simple_read():
    # Simple Read
    print("Reading example.txt")
    f = open(r"D:\GIS\Data\example.txt")
    for line in f:
        print(line)
    f.close()

def fileinput_read():
    # Use fileinput
    print("Reading example.txt using fileinput")
    infile = r"D:\GIS\Data\example.txt"
    for line in fileinput.input(infile):
        print(line)

def text_read_fc_create():
    # Read a text file and convert the entries to a point feature class
    fgdb = r"D:\GIS\Data\Data.gdb"
    infile = r"D:\GIS\Data\example.txt"
    fc = "trees"
    sr = arcpy.SpatialReference(2248)
    arcpy.env.workspace = fgdb

    arcpy.management.CreateFeatureclass(out_path=fgdb, out_name=fc, geometry_type="POINT", spatial_reference=sr)

    with arcpy.da.InsertCursor(in_table=fc, field_names=["SHAPE@"]) as cursor:

        with open(infile) as f:
            for line in f:
                _, x, y = line.split()
                point = arcpy.Point(float(x), float(y))
                cursor.insertRow([point])

def csv_read_fc_create():
    # Read a CSV and create a feature class
    print("Read a CSV and create a Feature Class.")
    fgdb = r"D:\GIS\Data\Data.gdb"
    infile = r"D:\GIS\Data\example.csv"
    fc = "trees_csv"
    sr = arcpy.SpatialReference(2248)
    arcpy.env.workspace = fgdb

    # arcpy.management.CreateFeatureclass(out_path=fgdb, out_name=fc, geometry_type="POINT", spatial_reference=sr)

    with arcpy.da.InsertCursor(in_table=fc, field_names=["SHAPE@"]) as cursor:

        with open(infile, mode='r', newline='') as f:
            reader = csv.reader(f)
            _ = next(reader) # Throw away the header
            for row in reader:
                print(row)
                point = arcpy.Point(float(row[1]), float(row[2]))
                cursor.insertRow([point])

def main():
    # simple_read()
    # fileinput_read()
    # text_read_fc_create()
    csv_read_fc_create()

if __name__ == '__main__':
    main()
=======
#---------------------------------------------------------------------------------------
# Name:        csv_example.py
# Purpose:     Examples of using CSV files
#
# Author:      Jesse Morgan
#
# Created:     03/02/2026
#---------------------------------------------------------------------------------------
import csv
import fileinput
import arcpy

def simple_read():
    # Simple Read
    print("Reading example.txt")
    f = open(r"D:\GIS\Data\example.txt")
    for line in f:
        print(line)
    f.close()

def fileinput_read():
    # Use fileinput
    print("Reading example.txt using fileinput")
    infile = r"D:\GIS\Data\example.txt"
    for line in fileinput.input(infile):
        print(line)

def text_read_fc_create():
    # Read a text file and convert the entries to a point feature class
    fgdb = r"D:\GIS\Data\Data.gdb"
    infile = r"D:\GIS\Data\example.txt"
    fc = "trees"
    sr = arcpy.SpatialReference(2248)
    arcpy.env.workspace = fgdb

    arcpy.management.CreateFeatureclass(out_path=fgdb, out_name=fc, geometry_type="POINT", spatial_reference=sr)

    with arcpy.da.InsertCursor(in_table=fc, field_names=["SHAPE@"]) as cursor:

        with open(infile) as f:
            for line in f:
                _, x, y = line.split()
                point = arcpy.Point(float(x), float(y))
                cursor.insertRow([point])

def csv_read_fc_create():
    # Read a CSV and create a feature class
    print("Read a CSV and create a Feature Class.")
    fgdb = r"D:\GIS\Data\Data.gdb"
    infile = r"D:\GIS\Data\example.csv"
    fc = "trees_csv"
    sr = arcpy.SpatialReference(2248)
    arcpy.env.workspace = fgdb

    # arcpy.management.CreateFeatureclass(out_path=fgdb, out_name=fc, geometry_type="POINT", spatial_reference=sr)

    with arcpy.da.InsertCursor(in_table=fc, field_names=["SHAPE@"]) as cursor:

        with open(infile, mode='r', newline='') as f:
            reader = csv.reader(f)
            _ = next(reader) # Throw away the header
            for row in reader:
                print(row)
                point = arcpy.Point(float(row[1]), float(row[2]))
                cursor.insertRow([point])

def main():
    # simple_read()
    # fileinput_read()
    # text_read_fc_create()
    csv_read_fc_create()

if __name__ == '__main__':
    main()
>>>>>>> Stashed changes
