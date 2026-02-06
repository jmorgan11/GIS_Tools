import arcpy
from arcpy.sa import *
import os

def main(raster, folder, precision):
    orig_raster = Raster(raster)
    desc = arcpy.Describe(orig_raster)
    
    new_raster = (Float(Int((orig_raster + 0.05) * 10))) / 10

    new_raster.save(os.path.join(folder, desc.name))
    
    print("Done.")

if __name__ == '__main__':
    test_raster = r"c:\Temp\DEM\usgs_dem.tif"
    out_folder = r"c:\Temp\Output"
    in_precision = 1
    
    main(
        raster=test_raster,
        folder=out_folder,
        precision=in_precision
    )
