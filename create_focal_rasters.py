"""Create focal 50 rasters for the Risk Rating 2.0 requirements.

General steps:

1. Create the following folder structure:
    Focal_Work
        NED_1_arcsec_source (tiles from USGS go here)
        NED_1_arcsec_working
            Buffered_Rasters
            Focal_Rasters
            Clipped_Rasters
            Final_Rasters
        NED_1_3_arcsec_source (tiles from USGS go here)
        NED_1_3_arcsec_working
            Buffered_Rasters
            Focal_Rasters
            Clipped_Rasters
            Final_Rasters
        Scripts

2. Download all the NED 1 Arcsec and NED 1/3 Arcsec rasters from the USGS AWS website.
   Store these in their respective folders inside of the 'Focal_Work' folder.

   a. List bucket contents: aws s3 ls s3://prd-tnm/StagedProducts/Elevation/ --human-readable --summarize --no-sign-request
   b. Download NED 1/3:
       aws s3 sync "s3://prd-tnm/StagedProducts/Elevation/13/TIFF/current/" . --exclude "*.db" --exclude "*.vrt" --exclude "*.gpkg" --exclude "*.xml" --exclude "*.jpg" --no-sign-request
   c. Download NED 1arc:
       aws s3 sync "s3://prd-tnm/StagedProducts/Elevation/1/TIFF/current/" . --exclude "*.db" --exclude "*.vrt" --exclude "*.gpkg" --exclude "*.xml" --exclude "*.jpg" --no-sign-request
   
3. Create a tile index that contains a field called 'tile_name' which contains the
   names of each tile. A field named 'location' should also exist with the absolute path
   to each tile.
   Name the tiles indexes: ned_1_3_tile_index.shp and ned_1_tile_index.shp.
   Store these in the scripts folder.
4. Ensure a county_boundaries shapefile exists in the Scripts folder.  Make sure all the features
   in the county_boundaries shapefile has a tile associated with it.  If not, put the name of the feature
   in skip_list variable below.  The county_boundaries shapefile should have a 'Place_Name' field that
   stores the county name and state abbreviate.  All spaces should be replaced with an _.  Ensure
   all diacritics are replace.
5. Use the raster_type variable to select which NED tiles you want to process.
6. The final focal 50 rasters will be located in 'Final_Rasters' folder.  All other rasters can be deleted.

Notes:
    - If only certain counties need to be exported, put their names in the 'county_list' list below.
    - All datasets should be GCS.
    - The program will not overwrite any datasets.  If a raster already exists, the program will skip it.
    - All hard coded paths are in the Variables section below.
    - There are some magic numbers in the program but they are related to the Risk Rating 2.0 requirements.
    - There is a 'raster_type' variable which represents processing the NED 1 arcsec or NED 1/3 arcsec rasters.
      Change this to reflect which rasters are being processed.

This program could be automated more and error catching added.  I'm leaving as is since this will be rarely ran.

Author: Jesse Morgan
Date: 4/5/2023
"""
import arcpy
import os
import sys
from arcpy.sa import *

# Change this value based on the raster arcsec to be processed.
# raster_type = "1_3"  # For 1/3 arcsec
raster_type = "1"  # For 1 arcsec

# Variables
path = r'D:\Focal_Work'
county_boundaries = os.path.join(path, 'Scripts', 'county_boundaries.shp')
buffered_rasters = os.path.join(path, 'NED_' + raster_type + '_arcsec_working\Buffered_Rasters')
focal_rasters = os.path.join(path, 'NED_' + raster_type + '_arcsec_working\Focal_Rasters')
tiles = os.path.join(path, "Scripts", "ned_" + raster_type + "_tile_index.shp")
main_folder = os.path.join(path, 'NED_' + raster_type + '_arcsec_source')
clipped_rasters = os.path.join(path, 'NED_' + raster_type + '_arcsec_working\Clipped_Rasters')
final_rasters = os.path.join(path, 'NED_' + raster_type + '_arcsec_working\Final_Rasters')

# Make feature layers
if arcpy.Exists("county_boundaries"):
    arcpy.Delete_management("county_boundaries")
county_boundaries_lyr = arcpy.MakeFeatureLayer_management(county_boundaries, "county_boundaries")

if arcpy.Exists("tiles"):
    arcpy.Delete_management("tiles")
tiles_lyr = arcpy.MakeFeatureLayer_management(tiles, "tiles")

# Get the count of the rows
row_count = int(arcpy.GetCount_management(county_boundaries)[0])
counter = 1

# Use this list if only certain counties should be exported.  Otherwise, leave the list empty.
county_list = []
if len(county_list) != 0:
    row_count = len(county_list)

# Use this list to skip counties.
skip_list = ['Rose_Island_AS', 'Swains_Island_AS']
if len(skip_list) != 0 and len(county_list) == 0:
    row_count -= len(skip_list)

# Iterate through the county boundaries
with arcpy.da.SearchCursor(county_boundaries_lyr, "Place_Name") as cursor:
    for row in cursor:
        county_name = row[0]

        # Check if only certain counties are to be processed.
        if len(county_list) != 0:
            if county_name not in county_list:
                continue

        # Check if a county is listed in the skip_list.
        if county_name in skip_list:
            print("\t...in skip_list. Skipping...")
            continue

        # Check to see if the final raster already exists.  If so, continue
        if arcpy.Exists(os.path.join(final_rasters, county_name + "_focal.tif")):
            print(f"{county_name} final raster already exists.  Skipping...")
            continue

        print(f"{county_name}: {counter} of {row_count}")
        raster_list = []

        # Select the current county
        current_county = arcpy.management.SelectLayerByAttribute(
            in_layer_or_view=county_boundaries_lyr,
            selection_type="NEW_SELECTION",
            where_clause="Place_Name = '" + county_name + "'")

        # Select intersecting tiles out to 1,000 feet.  This will cover the 500 feet requirement.
        selected_tiles = arcpy.management.SelectLayerByLocation(
            in_layer=tiles_lyr,
            overlap_type="WITHIN_A_DISTANCE",
            select_features=current_county,
            search_distance="1000 Feet",
            selection_type="NEW_SELECTION")

        # Append the paths to the raster_list
        with arcpy.da.SearchCursor(selected_tiles, "tile_name") as raster_cursor:
            for raster_row in raster_cursor:
                raster = raster_row[0]
                if raster_type == "1_3":
                    folder_name = raster.replace('USGS_13_', '')
                else:
                    folder_name = raster.replace('USGS_1_', '')
                raster_path = os.path.join(main_folder,
                                           folder_name.replace(".tif", ""),
                                           raster)
                if raster_path not in raster_list:
                    raster_list.append(raster_path)

        # Check the paths to the rasters exists.
        for r in raster_list:            
            if not os.path.exists(r):
                print(f"\tFAIL: '{r}' does not exist.")
                sys.exit(1)

        # Check for extra characters in the county name that could affect the naming of the rasters.
        if "-" in county_name:
            county_name = county_name.replace("-", "")
        if "'" in county_name:
            county_name = county_name.replace("'", "")
        if " " in county_name:
            county_name = county_name.replace(" ", "")                

        # Mosaic the rasters
        print("\t...creating mosaic...")
        buffer_raster = county_name + "_buffered.tif"
        arcpy.management.MosaicToNewRaster(
            input_rasters=raster_list,
            output_location=buffered_rasters,
            raster_dataset_name_with_extension=buffer_raster,
            number_of_bands=1,
            pixel_type="32_BIT_FLOAT")

        # Buffer the current county boundary.  600-meters will cover the 500-meter requirement.
        buffered_boundary = arcpy.analysis.Buffer(
            in_features=current_county,
            out_feature_class=r"in_memory\Buffer",
            buffer_distance_or_field="600 Meters",
            dissolve_option="ALL")

        # Clip the raster
        print("\t...clipping...")
        clipped_raster = os.path.join(clipped_rasters, county_name + "_clipped.tif")
        outExtractByMask = ExtractByMask(
            os.path.join(buffered_rasters, county_name + "_buffered.tif"),
            buffered_boundary,
            "INSIDE")
        outExtractByMask.save(clipped_raster)

        # Remove the buffer in memory
        arcpy.Delete_management(buffered_boundary)

        # Create Focal Raster.  Note: these are not compressed.
        print("\t...creating focal raster...")
        focal_raster = county_name + "_focal.tif"
        # 500-meter radius is needed. NED 1 arcsec cell size is about 30 meters.  NED 1/3 arcsec
        # cell size is about 10 meters. Therefore, use 500/30 = 16.67, rounded to 17 for NED 1 arsec.
        # Else use 50 for NED 1/3 arcsec (50 * 10 meter cell size = 500 meters).
        if raster_type == '1_3':
            cell_radius = 50
        else:
            cell_radius = 17
        neighborhood_type = NbrCircle(cell_radius, "CELL")  
        outFocalStatistics = FocalStatistics(
            in_raster=clipped_raster,
            neighborhood=neighborhood_type,
            statistics_type="MEAN",
            ignore_nodata="NODATA")
        outFocalStatistics.save(os.path.join(focal_rasters, focal_raster))

        # Compress the final raster by copying it.
        print("\t...compressing...")
        final_raster = os.path.join(final_rasters, county_name + "_focal.tif")
        arcpy.management.CopyRaster(
            in_raster=os.path.join(focal_rasters, focal_raster),
            out_rasterdataset=final_raster,
            pixel_type="32_BIT_FLOAT")

        # Delete the temporary rasters to save space.
        if arcpy.Exists(os.path.join(buffered_rasters, buffer_raster)):
            arcpy.Delete_management(os.path.join(buffered_rasters, buffer_raster))
        if arcpy.Exists(clipped_raster):
            arcpy.Delete_management(clipped_raster)
        if arcpy.Exists(os.path.join(focal_rasters, focal_raster)):
            arcpy.Delete_management(os.path.join(focal_rasters, focal_raster))     

        # Final message
        print("\t...done\n")
        counter += 1

print("\n\nEnd of line.")
