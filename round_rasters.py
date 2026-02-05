#---------------------------------------------------------------------------------------
# Name:        round_rasters.py
# Purpose:     Round float raster values.
#
# Author:      Jesse Morgan
#
# Created:     02/04/2026
# Copyright:   (c) jmorg 2026
#---------------------------------------------------------------------------------------
import arcpy
import sys

def round_raster():
    """(Float(Int(("CST_Dpth01pct" + 0.05) * 10))) / 10"""
    pass

def check_precision(in_precision):
    """
    Verify the precision is a number, greater than 0 and less then 6 and is an integer.

    Arguments:
        in_precision - the user entered precision

    Returns:
        the precision value as integer
    """
    # TODO: Verify value entered is a number.
    # TODO: Check the rounding value is less than 0 or greater than 6
    return precision


def main(precision):
    """
    Main function.

    Arguments:
        precision - the rounding value.
    """
    # Verify the precision value is good.
    check_precision(in_precision=precision)

    # TODO: Get output folder
    # TODO: Check if the output raster already exists
    # TODO: Round the raster to temp file if using raster calculator
    # TODO: if using raster calculator, copy the raster to compress it
    # TODO: Allow TIFs, Rasters in a Geodatabase and ArcGIS Grids.
    pass

if __name__ == '__main__':
    precision = 1

    main(precision)
