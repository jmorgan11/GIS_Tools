"""QC the elevation values of the FRP WSE grids with the cross sections."""
import arcpy
import os

def convert_to_points(xs, pbl, workspace):
    """
    Convert the cross sections to points where they intersect the profile baselines.

    parameters:
        xs - cross section feature class
        pbl - profile baseline feature class
        workspace - output workspace for the new feature class

    returns:
        The path to the new feature class that was created.

    """

    # Output path to the new feataure class
    intersect_fc = os.path.join(workspace, "xs_pbl_intersect")

    print("Intersecting cross sections and profile baselines...")

    # Intersect the cross sections and profile baselines
    arcpy.analysis.Intersect(
        in_features=[xs, pbl],
        out_feature_class=intersect_fc,
        join_attributes="ALL",
        output_type="POINT")

    # Return the path to the new feature class
    return intersect_fc


def convert_from_multipoint(in_fc):
    """
    Convert a multipoint feature.

    parameters:
        in_fc - the multipoint feature class

    returns:
        The path to the new feature class.
    """
    print("Converting multipart to single part...")

    # Get the path to the feature class
    fc_path = arcpy.Describe(in_fc).path

    # Path to the new feature class
    new_fc = os.path.join(fc_path, "xs_elev_qc")

    # Convert the multipart feature class
    arcpy.management.MultipartToSinglepart(
        in_features=in_fc,
        out_feature_class=new_fc)

    # Delete the multipart feature class
    arcpy.management.Delete(in_fc)

    # Return the path to the new featue class
    return new_fc


def drop_fields(in_fc):
    """
    Drop any unneeded fields.

    parameters:
        in_fc - the feature class to drop the fields from.

    returns:
        None
    """

    print("Dropping unneeded fields...")

    # Fields not to delete
    keep_fields = ["OBJECTID", "SHAPE", "XS_LN_ID", "WTR_NM", "STREAM_STN",
                   "XS_10pct", "XS_04pct", "XS_02pct", "XS_01pct", "XS_01plus",
                   "XS_0_2pct", "XS_01minus", "XS_01fut", "XS_50pct", "XS_20pct"]

    # Get a list of current fields
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Fields to drop
    drop_fields = [field for field in field_names if field not in keep_fields]

    # Drop the fields
    for drop_field in drop_fields:
        arcpy.management.DeleteField(
            in_table=in_fc,
            drop_field=drop_field,
            method="DELETE_FIELDS")


def extract_wse_values(in_rasters, in_fc, in_dem):
    """
    Extract the cell values from the rasters and the DEM and store them
    in the feature class.

    parameters:
        in_rasters - the rasters to extract values from.  Typically the WSE rasters.
        in_fc - the feature class to store the extracted values in.
        in_dem - the DEM

    returns:
        None
    """
    print("Extracting WSE values...")

    # Build up the raster list
    possible_raster_names = [
        "WSE_10pct", "WSE_04pct", "WSE_02pct", "WSE_01pct", "WSE_01plus",
        "WSE_0_2pct", "WSE_01minus", "WSE_01fut", "WSE_50pct", "WSE_20pct"]

    raster_list = []

    for raster_name in possible_raster_names:
        for in_raster in in_rasters:
            if raster_name in in_raster:
                print(f"\t{raster_name} will be extracted...")
                raster_list.append([in_raster, raster_name])

    # Add the DEM to the list of rasters to extract
    raster_list.append([in_dem, "DEM"])

    # Extract the raster cell values
    arcpy.sa.ExtractMultiValuesToPoints(
        in_point_features=in_fc,
        in_rasters=raster_list,
        bilinear_interpolate_values="NONE")


def calc_nulls(in_fc):
    """
    Calculate all the NULL fields to -9999.

    parameters:
        in_fc - the feature class to update

    returns:
        None
    """
    print("Calculating nulls to -9999...")

    # Fields to update
    field_list = [
        "XS_10pct", "XS_04pct", "XS_02pct", "XS_01pct", "XS_01plus", "XS_0_2pct", "XS_01minus",
        "XS_01fut", "XS_50pct", "XS_20pct", "WSE_10pct", "WSE_04pct", "WSE_02pct", "WSE_01pct",
        "WSE_01plus", "WSE_0_2pct", "WSE_01minus", "WSE_01fut", "WSE_50pct", "WSE_20pct" , "DEM"]

    # List of field names in the feature class
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Calc the fields
    for field in field_list:
        if field in field_names:
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=field + " IS NULL")

            arcpy.management.CalculateField(
                in_table=selected,
                field=field,
                expression="-9999")
    
def calc_diff_fields(in_fc):
    """
    Calculate the differences between the cross section elevation values and
    the WSE extracted values.

    parameters:
        in_fc - the feature class to update

    returns:
        None
    """
    print("Calculating difference fields...")

    field_groups = [
        ["XS_10pct", "WSE_10pct", "DIF_10pct"],
        ["XS_04pct", "WSE_04pct", "DIF_04pct"],
        ["XS_02pct", "WSE_02pct", "DIF_02pct"],
        ["XS_01pct", "WSE_01pct", "DIF_01pct"],
        ["XS_01plus", "WSE_01plus", "DIF_01plus"],
        ["XS_0_2pct", "WSE_0_2pct", "DIF_0_2pct"],
        ["XS_01minus", "WSE_01minus","DIF_01minus"],
        ["XS_01fut", "WSE_01fut", "DIF_01fut"],
        ["XS_50pct", "WSE_50pct", "DIF_50pct"],
        ["XS_20pct", "WSE_20pct", "DIF_20pct"]
        ]

    # List of field names in the feature class
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Iterate through the field pairs
    for pct, wse, dif in field_groups:
        if pct in field_names and wse in field_names:
            print(f"\tCalculating difference of {pct} and {wse}...")

            # Selected all the PCT and WSE rows that are not -9999
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=pct + " <> -9999 And " + wse + " <> -9999")

            # Calculate the absolute difference of the two fields
            arcpy.management.CalculateField(
                in_table=selected,
                field=dif,
                field_type="FLOAT",
                expression="round(abs(!" + pct + "!-!" + wse + "!), 1)")

            # Select all the DIF rows that are NULL
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=dif + " IS NULL")

            # Calculate them to -9999
            arcpy.management.CalculateField(
                in_table=selected,
                field=dif,
                expression="-9999")


def calc_diff_error(in_fc):
    """
    Calculate the differences between the cross section elevation values and
    the WSE extracted values are greater than 0.5.

    parameters:
        in_fc - the feature class to update

    returns:
        None
    """
    print("Calculating difference error...")

    # Fields to calculate
    diff_fields = ["DIF_10pct", "DIF_04pct", "DIF_02pct", "DIF_01pct",
                   "DIF_01plus", "DIF_0_2pct", "DIF_01minus",
                   "DIF_01fut", "DIF_50pct", "DIF_20pct"]

    # List of field names in the feature class
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Iterate through the fields
    for dif_field in diff_fields:
        if dif_field in field_names:
            error_field_name = dif_field.replace("DIF", "ERR")

            print(f"\tCalculating {error_field_name}...")

            # Add the ERR field
            arcpy.management.AddField(
                in_table=in_fc,
                field_name=error_field_name,
                field_type="TEXT",
                field_length=1)

            # Selected all rows with a DIF field value > 0.5
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=dif_field + " > 0.5 ")

            # Calculate the ERR field to T
            arcpy.management.CalculateField(
                in_table=selected,
                field=error_field_name,
                expression="'T'")

            # Selected all rows with a DIF field value <= 0.5
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=dif_field + " <= 0.5 ")

            # Calculate them to F
            arcpy.management.CalculateField(
                in_table=selected,
                field=error_field_name,
                expression="'F'")
            


def calc_scrv(in_fc, dem):
    """
    Calculate the Slope-Cell Resolution Value (SCRV):

    Elevation change / stream distance * cell size (“Slope-Cell Resolution Value” (SCRV))

    parameters:
        in_fc - the feature class to update
        dem - the DEM

    returns:
        None
    """
    print("Calculating the Slope-Cell Resolution Value...")

    # Get the cell size of the DEM
    desc = arcpy.Describe(dem)
    cellsize = desc.children[0].meanCellHeight

    # Get a list of unique stream names
    water_names = sorted(list(set([row[0] for row in arcpy.da.SearchCursor(in_fc, ["WTR_NM"])])))

    # Add the SCRV field
    arcpy.management.AddField(
        in_table=in_fc,
        field_name="SCRV",
        field_type="FLOAT")

    # Iterate through the water names
    for water_name in water_names:
        print(f"\tCalculating SCRV for {water_name}")

        # Create a list of lists where the elemnts are the stream station and DEM value
        station_list = [
            [row[0], row[1]] for row in arcpy.da.SearchCursor(
                in_fc, ["STREAM_STN", "DEM"], "WTR_NM = '" + water_name + "'")]

        # Sort the station list on the first element
        station_list = sorted(station_list, key = lambda x: x[0])

        # Iterate through the list and calcuate the SCRV
        for index in range(1, len(station_list)):

            # Get the current and previous station lists
            previous_station = station_list[index - 1]
            current_station = station_list[index]

            # Calculate the difference in distance and elevation
            distance = current_station[0] - previous_station[0]
            elevation_change = current_station[1] - previous_station[1]

            # Calculate the SCRV
            scrv = 0
            if distance != 0:
                scrv = elevation_change / distance * cellsize

            # Select the row that matches the stream station and water name
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause="WTR_NM = '" + water_name + "' And STREAM_STN = " + str(current_station[0]))

            # Calculate the selected row to the SCRV
            arcpy.management.CalculateField(
                in_table=selected,
                field="SCRV",
                expression=scrv)

    # Select all the rows with NULL SCRV
    selected = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=in_fc,
        where_clause="SCRV IS NULL")

    # Calculate the selected row to the SCRV
    arcpy.management.CalculateField(
        in_table=selected,
        field="SCRV",
        expression=-9999)            
    

def create_review_field(in_fc):
    """
    Add the review field based on the SCRV and ERR values
    
    parameters:
        in_fc - the feature class to update

    returns:
        None
    """
    print("Adding the Review field...")

    # Add the Review field
    arcpy.management.AddField(
        in_table=in_fc,
        field_name="REVIEW",
        field_type="TEXT",
        field_length=1)

    # Calculate all the rows to F for the Review field
    arcpy.management.CalculateField(
        in_table=in_fc,
        field="REVIEW",
        expression="'F'")

    # Potential ERR fields
    err_fields = ["ERR_10pct", "ERR_04pct", "ERR_02pct", "ERR_01pct", "ERR_01plus",
                  "ERR_0_2pct", "ERR_01minus", "ERR_01fut", "ERR_50pct", "ERR_20pct"]

    # List of field names in the feature class
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Iterate through the ERR fields
    for err_field in err_fields:
        if err_field in field_names:
            
            # Selected all rows with an ERR field 'T' and an SCRV value <= 0.3
            selected = arcpy.management.SelectLayerByAttribute(
                in_layer_or_view=in_fc,
                where_clause=err_field + " = 'T' And SCRV <= 0.3 And SCRV <> -9999")

            # Calculate the REVIEW field to T
            arcpy.management.CalculateField(
                in_table=selected,
                field="REVIEW",
                expression="'T'")

def export_final_fc(in_fc):
    """
    Export the final feature class by reordering the fields.

    parameters:
        in_fc - the feature class to export

    returns:
        None
    """
    print("Exporting the final feature class...")

    # Get the path to the feature class
    fc_path = arcpy.Describe(in_fc).path

    # Path to the new feature class
    new_fc = os.path.join(fc_path, "frp_xs_elev_qc")

    # List of field names in the feature class
    field_names = [field.name for field in arcpy.ListFields(dataset=in_fc)]

    # Field mappings
    field_map = ""
    
    xs_ln_id = f"XS_LN_ID \"XS_LN_ID\" true true false 25 Text 0 0,First,#,{in_fc},XS_LN_ID,0,24;"
    wtr_nm = f"WTR_NM \"WTR_NM\" true true false 100 Text 0 0,First,#,{in_fc},WTR_NM,0,99;"
    stream_stn = f"STREAM_STN \"STREAM_STN\" true true false 8 Double 0 0,First,#,{in_fc},STREAM_STN,-1,-1;"
    review = f"REVIEW \"REVIEW\" true true false 1 Text 0 0,First,#,{in_fc},REVIEW,0,0;"
    scrv = f"SCRV \"SCRV\" true true false 4 Float 0 0,First,#,{in_fc},SCRV,-1,-1;"
    dem = f"DEM \"DEM\" true true false 4 Float 0 0,First,#,{in_fc},DEM,-1,-1;"

    field_map = xs_ln_id + wtr_nm + stream_stn + review + scrv + dem

    for event in ['10pct','04pct', '02pct', '01pct', '01plus', '0_2pct', '01minus', '01fut', '50pct', '20pct']:
        xs = "XS_" + event
        if xs in field_names:
            xs_formatted = f"{xs} \"{xs}\" true true false 8 Double 0 0,First,#,{in_fc},{xs},-1,-1;"
            field_map += xs_formatted

        wse = "WSE_" + event
        if wse in field_names:
            wse_formatted = f"{wse} \"{wse}\" true true false 4 Float 0 0,First,#,{in_fc},{wse},-1,-1;"
            field_map += wse_formatted
        
        diff = "DIF_" + event
        if diff in field_names:
            diff_formatted = f"{diff} \"{diff}\" true true false 4 Float 0 0,First,#,{in_fc},{diff},-1,-1;"
            field_map += diff_formatted

        err = "ERR_" + event
        if err in field_names:
            err_formatted = f"{err} \"{err}\" true true false 1 Text 0 0,First,#,{in_fc},{err},0,0;"
            field_map += err_formatted

    # Export the feature class
    arcpy.conversion.ExportFeatures(
        in_features=in_fc,
        out_features=new_fc,
        field_mapping=field_map)                 

    # Delete the original feature class
    arcpy.management.Delete(in_fc)


def main(xs, pbl, workspace, rasters, dem):
    """
    Main function.

    parameters:
        xs - cross sections
        pbl - profile baselines
        workspace - output workspace
        rasters - WSE rasters to extract values from
        dem - the DEM

    returns:
        None
    """
    arcpy.env.overwriteOutput = True
   
    intersect_fc = convert_to_points(xs=xs, pbl=pbl, workspace=workspace)
    qc_fc = convert_from_multipoint(in_fc=intersect_fc)
    drop_fields(in_fc=qc_fc)
    extract_wse_values(in_rasters=rasters, in_fc=qc_fc, in_dem=dem)
    calc_nulls(in_fc=qc_fc)
    calc_diff_fields(in_fc=qc_fc)
    calc_diff_error(in_fc=qc_fc)
    calc_scrv(in_fc=qc_fc, dem=dem)
    create_review_field(in_fc=qc_fc)
    export_final_fc(in_fc=qc_fc)

if __name__ == '__main__':
    cross_sections = r'C:\GIS\Hiwassee_Watershed\Test\Code_Testing.gdb\xs_combined'
    profile_baselines = r'C:\GIS\Hiwassee_Watershed\20250902_FanninCo_GA_NOV_2022.gdb\FIRM_Spatial_Layers\S_Profil_Basln'
    out_workspace = r'C:\GIS\Hiwassee_Watershed\Test\Code_Testing.gdb'
    wse_rasters = [
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_0_2pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_01fut.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_01minus.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_01pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_01plus.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_02pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_04pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_10pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_20pct.tif',
        r'C:\GIS\Hiwassee_Watershed\WSE_Grids\WSE_50pct.tif'
    ]
    project_dem = r'C:\GIS\Hiwassee_Watershed\Bare_Earth_DEM\index_Terrain_processed3.vrt'
    
    main(
        xs=cross_sections,
        pbl=profile_baselines,
        workspace=out_workspace,
        rasters=wse_rasters,
        dem=project_dem
    )
