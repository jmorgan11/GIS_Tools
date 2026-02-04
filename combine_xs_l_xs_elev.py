"""
This script combines the L_XS_ELEV table values with the
S_XS table based on the XS_LN_ID field.  A new feature
class is created.

Author: Jesse Morgan
Created: 1/26/2026
"""
import arcpy
import os
import sys

def main(xs_fc, l_xs_table, out_loc):
    """
    main function

    parameters:
        xs_fc - input S_XS feature class
        l_xs_table - input L_XS_Elev table
        out_loc - output location of the combined S_XS and L_XS_Elev tables
    """
    try:
        arcpy.AddMessage("Combining S_XS and L_XS_ELEV tables...")

        # Determine the workspace type
        workspace_type = arcpy.Describe(out_loc).workspaceType

        # Set the output feature class name
        out_xs_fc = os.path.join(out_loc, "xs_combined")
        if workspace_type == "FileSystem":
            out_xs_fc += ".shp"

        # Copy out XS feature class to a shapefile
        if arcpy.Exists(out_xs_fc):
            arcpy.Delete_management(out_xs_fc)
        arcpy.management.CopyFeatures(xs_fc, out_xs_fc)

        # Add columns to the new feature class
        fields = ['PCT_10', 'PCT_4', 'PCT_2', 'PCT_1', 'PCT_1_Plus', 'PCT_0_2',
                  'PCT_1_Min', 'PCT_1_Fut', 'PCT_50', 'PCT_20']

        for field in fields:
            arcpy.management.AddField(
                in_table=out_xs_fc,
                field_name=field,
                field_type="DOUBLE")

        # Iterate through the cross-section
        with arcpy.da.UpdateCursor(
                in_table=out_xs_fc,
                field_names=['XS_LN_ID'] + fields) as cursor:
            for row in cursor:
                xs_ln_id = row[0]

                # Create the query
                sql_exp = """{0} = '{1}'""".format(
                    arcpy.AddFieldDelimiters(
                        datasource=l_xs_table,
                        field='XS_LN_ID'),
                    xs_ln_id)

                # Find the match L_XS_Elev values
                with arcpy.da.SearchCursor(
                        in_table=l_xs_table,
                        field_names=["EVENT_TYP", "WSEL"],
                        where_clause=sql_exp) as l_cursor:
                    for l_row in l_cursor:
                        event_type = l_row[0]
                        wsel = l_row[1]

                        if event_type in ('10pct', '10 Percent Chance'):
                            row[1] = wsel
                        elif event_type in ('04pct', '4 Percent Chance'):
                            row[2] = wsel
                        elif event_type in ('02pct', '2 Percent Chance'):
                            row[3] = wsel
                        elif event_type in ('01pct', '1 Percent Chance'):
                            row[4] = wsel
                        elif event_type in ('01plus', '1 Percent Plus Chance'):
                            row[5] = wsel
                        elif event_type in ('0_2pct', '0.2 Percent Chance'):
                            row[6] = wsel
                        elif event_type in ('01minus', '1 Percent Minus Chance'):
                            row[7] = wsel
                        elif event_type in ('01pctfut', '1 Percent Change Future Conditions'):
                            row[8] = wsel
                        elif event_type in ('50pct', '50 Percent Chance'):
                            row[9] = wsel
                        elif event_type in ('20pct', '20 Percent Chance'):
                            row[10] = wsel
                    cursor.updateRow(row)

        arcpy.AddMessage("Output: " + out_xs_fc)
        arcpy.AddMessage("Done")

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))


if __name__ == '__main__':
    s_xs_fc = sys.argv[1]
    l_xs_elev_table = sys.argv[2]
    out_location = sys.argv[3]

    main(xs_fc=s_xs_fc,
         l_xs_table=l_xs_elev_table,
         out_loc=out_location)
