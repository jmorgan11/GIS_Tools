"""
Round a raster to a specified precision.

Author: Jesse Morgan
Created: 2/16/2026
"""
import sys
import os
import arcpy
from arcpy.sa import Raster, Float, Int


def determine_precision(in_prec):
    """
    Determines the value to use for the precision.

    parameters:
        in_prec - the number of decimal places to round to

    returns:
        rounding_value - the initial value to add for rounding
        multiplier - used to shift the mantissa"""
    try:
        precision = int(in_prec)

    except ValueError:
        print("ERROR: Precision must be number between 0 and 5.")
        sys.exit(1)

    rounding_value = 0
    multiplier = 0

    if precision < 0:
        print("ERROR: Precision value must not be negative.")
        sys.exit(1)

    if precision > 5:
        print("ERROR: Precision value must not be greater than 5.")
        sys.exit(1)

    if precision > 0:
        rounding_value = 5 / 10 ** (precision + 1)
        multiplier = 1 * 10 ** precision

    return rounding_value, multiplier

def main(rasters, out_workspace, precision):
    """
    main function

    parameters:
        rasters - list of rasters to round
        out_workspace - output location for the rounded rasters
        precision - how many decimal places to round to
    """
    try:
        for raster in rasters:
            # Get raster information
            orig_raster = Raster(raster)
            desc = arcpy.Describe(orig_raster)
            in_raster_name = desc.name
            extension = desc.extension

            # Create place holders for new rasters
            new_raster = None
            final_raster = None

            # Determine out raster
            out_desc = arcpy.Describe(out_workspace)


            if out_desc.dataElementType == "DEWorkspace":  # Output is a file geodatabase
                out_raster_name = in_raster_name.replace(extension, "")  # Remove extension
                new_raster = os.path.join(out_workspace, out_raster_name)
            else:
                out_raster_name = "temp_" + desc.name  # Temp raster to copy later

                if not extension:  # The input raster was in a file geodatabase
                    extension = ".tif"

                new_raster = os.path.join(out_workspace, out_raster_name + extension)
                final_raster = os.path.join(out_workspace, in_raster_name + extension)

            # Check if the output raster already exists.
            if arcpy.Exists(new_raster) or arcpy.Exists(final_raster):
                print(f"ERROR: {new_raster} already exists. Exiting...")
                sys.exit(1)

            # Get the values for the rounding formula
            rounding_value, multiplier = determine_precision(precision)

            # Round the raster
            rounded_raster = (Float(Int((orig_raster + rounding_value) * multiplier))) / multiplier
            rounded_raster.save(new_raster)

            # If the output workspace is a folder, copy the raster to invoke the LZW compression
            if out_raster_name.startswith("temp"):
                arcpy.management.CopyRaster(
                    in_raster=new_raster,
                    out_rasterdataset=final_raster)
                arcpy.management.Delete(new_raster)

    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))


if __name__ == '__main__':
    in_rasters = sys.argv[1].split(';')
    workspace = sys.argv[2]
    in_precision = sys.argv[3]

    main(
        rasters=in_rasters,
        out_workspace=workspace,
        precision=in_precision
    )
