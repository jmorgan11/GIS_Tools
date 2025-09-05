"""Make WSE grids for Flood Risk Products"""
import os
import arcpy
from arcpy.sa import *

def create_polygon(in_xs_path, station_1, station_2, out_fc):
    """
    Create an in memory polygon of that covers two cross sections.
    The polygon will be merged into a larger polygon to create
    the clipper.

    Keyword arguments:
    in_xs_path -- the full path to the cross section feature class
    station_1 -- the lower station of a single cross section
    station_2 -- the next station of a single cross section
    out_fc -- the feature class to append the in memory polgon to
    """
    try:
        sel_station = str(station_1) + ", " + str(station_2)

        xs_sel = arcpy.management.MakeFeatureLayer(
            in_features=in_xs_path,
            out_layer="xs_sel",
            where_clause='"STREAM_STN" IN(' + sel_station + ")")

        boundary = arcpy.management.MinimumBoundingGeometry(
            in_features=xs_sel,
            out_feature_class="in_memory\\clip_boundary",
            geometry_type="CONVEX_HULL",
            group_option="ALL")


        # Append the polgyon to the clipper feature class
        arcpy.management.Append(inputs=boundary,
                                target=out_fc,
                                schema_type="NO_TEST")

    finally:
        # Delete the temporary objects
        arcpy.management.Delete(in_data="in_memory\\clip_boundary")
        arcpy.management.Delete(in_data="xs_sel")


def create_stream_clippers(workspace, water_name, coord_sys):
    """
    Create a bounding polygon for each stream.

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream.  Will be converted to a folder name
    coord_sys -- the coordinate system to use for the clipper
    """

    # Final shapefile to be created
    table_name = arcpy.ValidateTableName(water_name).lower()
    clipper = os.path.join(workspace, table_name, "clipper.shp")
    xs_layer = os.path.join(workspace, table_name, "xs_elev.shp")

    if arcpy.Exists(dataset=clipper):
        arcpy.AddMessage("\t\tClipper.shp already exists.")
        return

    # Create a temporary shapefile to hold each boundary
    clipper_temp = arcpy.CreateFeatureclass_management(
        out_path=workspace,
        out_name="clipper_temp.shp",
        geometry_type="POLYGON",
        spatial_reference=coord_sys)

    # Create a sorted list of the stream stations for the folder's s_xs.shp
    station_list = []
    with arcpy.da.SearchCursor(in_table=xs_layer,
                               field_names="STREAM_STN") as cursor:
        for row in cursor:
            if row[0] not in station_list:
                station_list.append(row[0])

    station_list = sorted(station_list)

    # Iterate through the stream station list sending every two
    # stations to the create_polygon function
    for station in range(0, len(station_list) - 1):
        create_polygon(in_xs_path=xs_layer,
                       station_1=station_list[station],
                       station_2=station_list[station + 1],
                       out_fc=clipper_temp)

    # Dissolve the features and remove the temporary shapefile
    arcpy.management.Dissolve(in_features=clipper_temp,
                              out_feature_class=clipper)

    # Delete the temporary objects
    arcpy.management.Delete(in_data=clipper_temp)


def make_tin(workspace, water_name, event, coord_sys):
    """Create a TIN for a stream based on a event.

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream.  Will be converted to a folder name
    event -- the flooding event to create the TIN for
    coord_sys -- the coordinate system to use for the clipper
    """

    try:
        table_name = arcpy.ValidateTableName(water_name).lower()
        xs_fc = os.path.join(workspace, table_name, "xs_elev.shp")
        out_tin = os.path.join(workspace, table_name, event.lower() + ".tin")

        # Make a feature layer for the current streams cross-sections
        if arcpy.Exists(dataset="xs_lyr"):
            arcpy.management.Delete(in_data="xs_lyr")

        # Query the cross-sections
        query_field = arcpy.AddFieldDelimiters(datasource=xs_fc, field=event)
        query = f"{query_field} NOT IN (-9999, -8888)"

        xs_layer = arcpy.management.MakeFeatureLayer(in_features=xs_fc,
                                                     out_layer="xs_lyr",
                                                     where_clause=query)


        # If there are at least 2 cross-sections, make the TIN
        if int(arcpy.management.GetCount(xs_layer)[0]) > 1:
            features = [[xs_layer, event, "Hard_Line", "<None>"]]

            arcpy.ddd.CreateTin(out_tin=out_tin,
                                spatial_reference=coord_sys,
                                in_features=features,
                                constrained_delaunay="DELAUNAY")
        else:
            arcpy.AddMessage(f"\t\tThere are no WSE values for {event}.")

    finally:
        arcpy.management.Delete(in_data="xs_lyr")
        arcpy.management.Delete(in_data="clipper_lyr")


def copy_cross_sections(workspace, water_name, xs_fc, coord_sys):
    """Copy the cross-sections for the stream to the stream's folder

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream.  Will be converted to a folder name
    xs_fc -- the cross section feature class
    coord_sys -- the coordinate system to use the new feature class
    """

    try:
        # Final shapefile to be created.
        table_name = arcpy.ValidateTableName(water_name).lower()
        xs_elev_fc = os.path.join(workspace, table_name, "xs_elev.shp")

        if arcpy.Exists(dataset=xs_elev_fc):
            arcpy.AddMessage("\t\tThe xs_elev.shp already exists.")
            return

        # Select the cross-sections for the current stream
        query_field = arcpy.AddFieldDelimiters(datasource=xs_fc, field="WTR_NM")
        query = f"{query_field} = '{water_name}'"
        xs_select = arcpy.management.MakeFeatureLayer(in_features=xs_fc,
                                                      out_layer="xs_select",
                                                      where_clause=query)

        # Project the current S_XS feature class to the workspace
        arcpy.management.Project(in_dataset=xs_select,
                                 out_dataset=xs_elev_fc,
                                 out_coor_system=coord_sys)

        # Create needed views
        xs_layer = arcpy.management.MakeFeatureLayer(in_features=xs_elev_fc,
                                                     out_layer="xs_layer")

        # Fields to add
        add_fields = ["WSE_50pct", "WSE_20pct", "WSE_10pct", "WSE_04pct",
                      "WSE_02pct", "WSE_01plus", "WSE_01min", "WSE_01pct",
                      "WSE_0_2pct", "WSE_0_5pct"]

        for field in add_fields:
            arcpy.AddField_management(xs_layer, field, "DOUBLE")
            arcpy.CalculateField_management(xs_layer, field, "-8888")

    finally:
        # Delete the view
        arcpy.management.Delete(in_data="xs_select")
        arcpy.management.Delete(in_data="xs_layer")


def create_elev_values_table(workspace, water_name, l_xs_table):
    """Append L_XS_Elev to S_XS.

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream.  Will be converted to a folder name
    l_xs_table -- the xs elevation table
    """

    try:
        # The reach's cross section feature class
        table_name = arcpy.ValidateTableName(water_name).lower()
        xs_elev_fc = os.path.join(workspace, table_name, "xs_elev.shp")

        # Create needed views
        xs_layer = arcpy.management.MakeFeatureLayer(in_features=xs_elev_fc,
                                                     out_layer="xs_layer")
        elev_layer = arcpy.management.MakeTableView(l_xs_table, "elev_layer")

        # Fields to process
        fields = ["XS_LN_ID", "WSE_50pct", "WSE_20pct", "WSE_10pct",
                  "WSE_04pct", "WSE_02pct", "WSE_01plus", "WSE_01min",
                  "WSE_01pct", "WSE_0_2pct", "WSE_0_5pct"]

        # Calculate the WSE values for each event
        with arcpy.da.UpdateCursor(xs_layer, fields) as update_cursor:
            for update_row in update_cursor:
                xs_ln_id = update_row[0]

                query_field = arcpy.AddFieldDelimiters(datasource=xs_elev_fc,
                                                       field="XS_LN_ID")
                query = f"{query_field} = '{xs_ln_id}'"

                with arcpy.da.SearchCursor(
                    in_table=elev_layer,
                    field_names=["EVENT_TYP", "WSEL", "EVAL_LN"],
                    where_clause=query,
                ) as search_cursor:
                    for search_row in search_cursor:
                        event_type = search_row[0]
                        wsel = search_row[1]
                        if event_type in ("50pct", "50 Percent Chance"):
                            update_row[1] = wsel
                        if event_type in ("20pct", "20 Percent Chance"):
                            update_row[2] = wsel
                        if event_type in ("10pct", "10 Percent Chance"):
                            update_row[3] = wsel
                        if event_type in ("04pct", "4 Percent Chance"):
                            update_row[4] = wsel
                        if event_type in ("02pct", "2 Percent Chance"):
                            update_row[5] = wsel
                        if event_type in ("01plus", "1 Percent Plus Chance"):
                            update_row[6] = wsel
                        if event_type in ("01minus", "1 Percent Minus Chance"):
                            update_row[7] = wsel
                        if event_type in ("01pct", "1 Percent Chance"):
                            update_row[8] = wsel
                        if event_type in ("0_2pct", "0.2 Percent Chance"):
                            update_row[9] = wsel
                        if event_type in ("0_5pct", "0.5 Percent Chance"):
                            update_row[10] = wsel

                        # Delete any 2D evaluation lines
                        if search_row[2] == "T":
                            update_cursor.deleteRow()
                        else:
                            update_cursor.updateRow(update_row)
    finally:
        arcpy.management.Delete(in_data="xs_layer")
        arcpy.management.Delete(in_data="elev_layer")


def make_folder(workspace, folder_name):
    """Make the folder for the current stream

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    folder_name -- the water name that will become the folder name
    l_xs_table -- the xs elevation table
    """
    new_folder_name = arcpy.ValidateTableName(folder_name).lower()

    if not arcpy.Exists(dataset=workspace + "\\" + new_folder_name):
        arcpy.management.CreateFolder(out_folder_path=workspace,
                                      out_name=new_folder_name)

    else:
        arcpy.AddMessage("\t\tFolder already exists.")


def create_flooding_clippers(workspace, flooding, buffer_size,
                             units, event, coord_sys):
    """Creates the clipping polygons.

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    flooding -- the flooding feature class
    buffer_size -- the distance to buffer the flooding
    units -- the units for the buffer
    event -- the event of the flooding to create
    coord_sys -- the coordinate system to use for the clipper
    """

    # Field deliminators
    fld_zone_field = arcpy.AddFieldDelimiters(datasource=flooding,
                                              field="FLD_ZONE")
    zone_subtype_field = arcpy.AddFieldDelimiters(datasource=flooding,
                                                  field="ZONE_SUBTY")

    # Check if the clipper already exists.  If so, skip it.
    query = None
    buffered_flooding = None
    if event == "100 year":
        buffered_flooding = workspace + "\\" + "flooding_1pct.shp"
        query = fld_zone_field + " in ('AE', 'A', 'AH')"
    if event == "500 year":
        buffered_flooding = workspace + "\\" + "flooding_0_2pct.shp"
        query = (zone_subtype_field
                 + " IN ('0500', '0.2 PCT ANNUAL CHANCE FLOOD HAZARD') OR "
                 + fld_zone_field + " IN ('AE', 'A', 'AH')")

    if arcpy.Exists(dataset=buffered_flooding):
        arcpy.AddMessage(f"\t\t{event.title()} flooding clipper already exists.")
        return

    try:
        # Make the feature layer
        flood_lyr = arcpy.management.MakeFeatureLayer(in_features=flooding,
                                                      out_layer="flood_lyr",
                                                      where_clause=query)

        # Project the flooding
        projected_flooding = workspace + "\\flooding_projected.shp"
        arcpy.management.Project(in_dataset=flood_lyr,
                                 out_dataset=projected_flooding,
                                 out_coor_system=coord_sys)

        # Buffer the flooding
        buffer_distance = str(float(buffer_size) * 0.50) + " " + units
        arcpy.analysis.Buffer(in_features=projected_flooding,
                              out_feature_class=buffered_flooding,
                              buffer_distance_or_field=buffer_distance,
                              dissolve_option="ALL")

    finally:
        # Delete the temporary, projected layer
        arcpy.management.Delete(in_data=projected_flooding)
        arcpy.management.Delete(in_data="flood_lyr")


def create_full_with_raster(workspace, water_name, event, cell_size):
    """Make the full width raster for the current WSE TIN

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream being processed
    event -- the event of the flooding to create
    cell_size -- the cell size of the output rasters
    """
    table_name = arcpy.ValidateTableName(water_name).lower()
    tin = os.path.join(workspace, table_name, event + ".tin")
    clipper = os.path.join(workspace, table_name, "clipper.shp")
    temp_wsel = os.path.join(workspace, table_name, event + "_temp.tif")
    out_wsel = os.path.join(workspace, table_name, event + "_full.tif")

    try:
        # Return if the full raster already exists.
        if arcpy.Exists(dataset=out_wsel):
            arcpy.AddMessage(f"\t\tRaster for {event} already exists.")
            return

        # Check if the TIN exists. If not, just return
        if not arcpy.Exists(dataset=tin):
            arcpy.AddMessage(f"\t\tThere are no WSE values for {event}.")
            return

        # Convert the TIN to a raster
        arcpy.ddd.TinRaster(in_tin=tin, out_raster=temp_wsel, data_type="FLOAT",
                            method="NATURAL_NEIGHBORS",
                            sample_distance="CELLSIZE " + str(cell_size))

        # Extract the temp raster by the clipper boundary
        clipper_lyr = arcpy.management.MakeFeatureLayer(in_features=clipper,
                                                        out_layer="clipper_lyr")
        out_extract = ExtractByMask(in_raster=temp_wsel, in_mask_data=clipper_lyr,
                                    extraction_area="INSIDE")
        out_extract.save(out_wsel)

    finally:
        # Delete temporary raster and TIN
        if arcpy.Exists(dataset=temp_wsel):
            arcpy.management.Delete(in_data=temp_wsel)
        if arcpy.Exists(dataset=tin):
            arcpy.management.Delete(in_data=tin)
        if arcpy.Exists(dataset="clipper_lyr"):
            arcpy.management.Delete(in_data="clipper_lyr")


def clip_raster(workspace, water_name, event):
    """Clip a raster to polygon.

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream being processed
    event -- the event of the flooding to create
    """

    table_name = arcpy.ValidateTableName(water_name)
    full_raster = os.path.join(workspace,table_name.lower(),
                               event + "_full.tif")
    clipped_raster = os.path.join(workspace, table_name, event + ".tif")

    # Skip if the rasters already exists
    if arcpy.Exists(dataset=clipped_raster):
        arcpy.AddMessage(f"\t\tThe clipped raster for {event} already exists.")
        return

    # Return if the full raster grid does not exists
    if not arcpy.Exists(dataset=full_raster):
        arcpy.AddMessage(f"\t\tThere are no WSE values for {event}.")
        return

    # Determine which flooding clipper to use.
    flooding = workspace + "\\" + "\\flooding_1pct.shp"

    if event in ("WSE_01plus", "WSE_01min", "WSE_0_2pct", "WSE_0_5pct"):
        flooding = workspace + "\\" + "\\flooding_0_2pct.shp"

    # Create a feature layer of the flooding
    flooding_layer = arcpy.management.MakeFeatureLayer(
        in_features=flooding, out_layer="flooding_layer")

    # Extract the raster by the flooding mask
    out_extract_mask = arcpy.sa.ExtractByMask(in_raster=full_raster,
                                              in_mask_data=flooding_layer,
                                              extraction_area="INSIDE")
    out_extract_mask.save(clipped_raster)

    # Delete the full raster
    arcpy.management.Delete(in_data=full_raster)
    arcpy.management.Delete(in_data="flooding_layer")


def extract_raster_from_dem(workspace, water_name, event, dem):
    """Extract raster from the DEM

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    water_name -- the current stream being processed
    event -- the event of the flooding to create
    dem -- the digital elevation model of the terrain
    """
    table_name = arcpy.ValidateTableName(water_name)
    full_raster = os.path.join(workspace, table_name.lower(), event + ".tif")
    temp_raster = os.path.join(workspace, table_name, event + "_temp.tif")

    # Return if the raster does not exists
    if not arcpy.Exists(dataset=full_raster):
        arcpy.AddMessage(f"\t\tThere are no WSE values for {event}.")
        return

    # Rename the clipped raster to temp raster for processing
    arcpy.management.Rename(in_data=full_raster, out_data=temp_raster)

    # Create the needed raster layers
    temp_raster_layer = arcpy.Raster(temp_raster)
    dem_layer = arcpy.Raster(dem)

    # Set NULL all values less than the DEM
    out_set_null = arcpy.sa.SetNull(
        in_conditional_raster=(temp_raster_layer < dem_layer),
        in_false_raster_or_constant=temp_raster_layer)

    out_set_null.save(full_raster)

    # Delete the temp raster
    arcpy.management.Delete(in_data=temp_raster)


def mosaic_wse_grid(workspace, event):
    """Mosaic all the rasters together by event

    Keyword arguments:
    workspace -- the workspace that contains the folders of stream names
    event -- the event of the flooding to create
    """
    # List of raster paths that will be mosaicked.
    raster_list = []

    # Final output raster
    target_raster = workspace + '\\' + event + '.tif'

    # Delete the target raster if it already exists.
    if arcpy.Exists(dataset=target_raster):
        arcpy.management.Delete(in_data=target_raster)

    # Get a list of rasters by event type.
    walk = arcpy.da.Walk(workspace=workspace,
                         datatype='RasterDataset',
                         type='TIF')

    for dirpath, _, filenames in walk:
        for filename in filenames:
            if event in filename:
                raster_list.append(dirpath + '\\' + filename)

    # Return if the list is empty
    if not raster_list:
        arcpy.AddMessage(f"\tThere are no WSE values for {event}.")
        return

    # Copy the first raster as the target raster.
    arcpy.management.Copy(in_data=raster_list[0], out_data=target_raster)

    # Mosaic the rasters together.
    arcpy.management.Mosaic(inputs=raster_list,
                            target=target_raster,
                            mosaic_type='MAXIMUM')


def main(xs_fc, flooding, process_list, elev_table, events, dem,
         coord_sys, cell_size, out_folder, mosaic):
    """The main function

    Keyword arguments:
    xs_fc -- the cross-section feature class (S_XS)
    flooding -- the flooding feature class (S_FLD_HAZ_AR)
    process_list -- stream names to process
    elev_table -- the cross-section elevation table (L_XS_ELEV)
    events -- the flood events to process
    dem -- the digital elevation model of the terrain
    coord_sys -- the final coordinate system of the data to be created
    cell_size -- the final cell size of the rasters
    out_folder -- the folder where all data processing will occur
    mosaic -- boolean stating whether to make the mosaicked rasters
    """

    # Set the snap raster for the raster processing
    arcpy.env.snapRaster = dem

    # coord_sys is received as string.  Convert it to spatial reference
    spatial_ref = arcpy.SpatialReference()
    spatial_ref.loadFromString(coord_sys)

    spatial_units = None
    if "foot" in spatial_ref.linearUnitName.lower():
        spatial_units = "Feet"
    elif "meter" in spatial_ref.linearUnitName.lower():
        spatial_units = "Meters"

    # Create the clippers of the flooding extents
    arcpy.AddMessage("Creating 1% flooding clipper.")
    create_flooding_clippers(workspace=out_folder, flooding=flooding,
                             buffer_size=cell_size, units=spatial_units,
                             event="100 year", coord_sys=spatial_ref)

    arcpy.AddMessage("Creating 0.2% flooding clipper.")
    create_flooding_clippers(workspace=out_folder, flooding=flooding,
                             buffer_size=cell_size, units=spatial_units,
                             event="500 year", coord_sys=spatial_ref)

    # Process each water name
    for water_name in process_list:
        arcpy.AddMessage(f"\nProcessing {water_name}:")

        arcpy.AddMessage("\tMaking reach folder.")
        make_folder(workspace=out_folder, folder_name=water_name)

        arcpy.AddMessage("\tCopying cross sections to reach folder.")
        copy_cross_sections(workspace=out_folder, water_name=water_name,
                            xs_fc=xs_fc, coord_sys=spatial_ref)

        arcpy.AddMessage("\tCombining XS and L_XS_Elev table.")
        create_elev_values_table(workspace=out_folder, water_name=water_name,
                                 l_xs_table=elev_table)

        arcpy.AddMessage("\tCreating the clipper boundary.")
        create_stream_clippers(
            workspace=out_folder, water_name=water_name, coord_sys=spatial_ref)

        for event in events:
            arcpy.AddMessage('\n')
            arcpy.AddMessage(f"\tCreating TIN for {event}.")
            make_tin(workspace=out_folder, water_name=water_name, event=event,
                     coord_sys=spatial_ref)

            arcpy.AddMessage(f"\tCreating a raster for {event}.")
            create_full_with_raster(workspace=out_folder, water_name=water_name,
                                    event=event, cell_size=cell_size)

            arcpy.AddMessage(f"\tClipping the {event} raster to the flooding extent.")
            clip_raster(workspace=out_folder, water_name=water_name,
                        event=event)

            if event not in ("WSE_01pct", "WSE_0_2pct"):
                arcpy.AddMessage(f"\tExtracting {event} from the DEM.")
                extract_raster_from_dem(workspace=out_folder,
                                        water_name=water_name,
                                        event=event, dem=dem)
    if mosaic:
        arcpy.AddMessage("\n")
        for event in events:
           arcpy.AddMessage(f"Mosaic rasters for the {event} event.")
           mosaic_wse_grid(workspace=out_folder, event=event)


if __name__ == "__main__":
    XS_FEATURE_CLASS = arcpy.GetParameterAsText(0)
    FLOODING_FEATURE_CLASS = arcpy.GetParameterAsText(1)
    L_XS_ELEV_TABLE = arcpy.GetParameterAsText(2)
    PROCESS_NAMES_LIST = arcpy.GetParameterAsText(3).split(";")
    PROCESS_NAMES = [name.replace("'", "") for name in PROCESS_NAMES_LIST]
    EVENTS_PARAM_LIST = arcpy.GetParameterAsText(4).split(";")
    EVENTS_LIST = [event.replace("'", "") for event in EVENTS_PARAM_LIST]
    OUT_CELL_SIZE = float(arcpy.GetParameterAsText(5))
    DEM_RASTER = arcpy.GetParameterAsText(6)
    OUTPUT_FOLDER = arcpy.GetParameterAsText(7)
    COORD_SYS = arcpy.GetParameterAsText(8)
    MAKE_MOSAIC = arcpy.GetParameterAsText(9)
    if MAKE_MOSAIC.lower() == 'true':
        MAKE_MOSAIC = True
    else:
        MAKE_MOSAIC = False

    main(xs_fc=XS_FEATURE_CLASS, flooding=FLOODING_FEATURE_CLASS,
         process_list=PROCESS_NAMES, elev_table=L_XS_ELEV_TABLE,
         events=EVENTS_LIST, dem=DEM_RASTER, cell_size=OUT_CELL_SIZE,
         coord_sys=COORD_SYS, out_folder=OUTPUT_FOLDER, mosaic=MAKE_MOSAIC)
