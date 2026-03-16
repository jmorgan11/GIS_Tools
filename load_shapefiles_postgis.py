import os
import subprocess
import glob

# Configuration
shp_dir = r'C:\Temp\buildings'
db_name = 'USA_Structures_Buildings'
db_user = 'postgres'
db_host = 'localhost'
db_port = '5432'
schema = 'public'
srid = '4326'

# Find all .shp files
shapefiles = glob.glob(os.path.join(shp_dir, '*.shp'))

for shp in shapefiles:
    # Use filename as table name
    table_name = os.path.splitext(os.path.basename(shp))[0]

    print(f"Loading {table_name}...")

    # 1. Generate SQL from shapefile (-I = GIST Index, -s = SRID, -d = drop/recreate)
    # 2. Pipe into psql
    cmd = (
        f"shp2pgsql -I -d -s {srid} \"{shp}\" {schema}.{table_name} | "
        f"psql -h {db_host} -p {db_port} -d {db_name} -U {db_user}"
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Successfully loaded {table_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to load {table_name}: {e}")

print("All tasks completed.")
