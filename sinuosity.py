"""
Report the sinuosity of line segments in a vector dataset.

Author: Jesse Morgan
Date: 11/9/2025
"""
import arcpy
import math
import sys

try:
    # Dataset with the lines to process
    fc_dataset = sys.argv[1]

    def sinuosity(in_shape):
        """Calculate the sinuosity of a shape."""

        # Full length of the input shape
        shape_length = in_shape.length

        # Deltas of the X and Y coordinates for the first and last points
        delta_x = in_shape.firstPoint.X - in_shape.lastPoint.X
        delta_y = in_shape.firstPoint.Y - in_shape.lastPoint.Y

        # Calculate the straight distance of the input shape
        straight_length = math.sqrt(pow(delta_x, 2) + pow(delta_y, 2))

        return shape_length / straight_length

    # Iterate through the features in the vector dataset
    with arcpy.da.SearchCursor(
        in_table=fc_dataset,
        field_names=["OID@", "SHAPE@"]) as cursor:

        for row in cursor:
            sin_index = sinuosity(row[1])

            print(f"OID: {row[0]}\tSinuosity Index: {round(sin_index, 2)}")
        

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
