#---------------------------------------------------------------------------------------
# Name:        csv_example.py
# Purpose:     Examples of using CSV files
#
# Author:      Jesse Morgan
#
# Created:     03/02/2026
#---------------------------------------------------------------------------------------
import fileinput
import arcpy

def main():

    # Simple Read
    print("Reading example.txt")
    f = open("example.txt")
    for line in f:
        # print(line)
        continue
    f.close()

    # Use fileinput
    print("Reading example.txt using fileinput")
    infile = "example.txt"
    for line in fileinput.input(infile):
        # print(line)
        continue

    # Read a text file and convert the entries to a point feature class
    fgdb = "Data.gdb"
    infile = "example.txt"
    fc = "trees"
    sr = arcpy.SpatialReference(2248)
    arcpy.env.workspace = fgdb

    arcpy.management.CreateFeatureclass(fgdb, fc, "Point", "", "", "", sr)

    with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cursor:

        with open(infile) as f:
            for line in f:
                ID, X, Y = line.split()
                print(ID, X, Y)
                point = arcpy.Point(X, Y)
                cursor.insertRow([point])

if __name__ == '__main__':
    main()
