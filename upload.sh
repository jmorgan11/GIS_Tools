#!/bin/bash
#
for file in *.shp; do
	if [ -f "$file" ]; then
		echo "Processing file: $file"
		shp2pgsql -s 4326 -I -e $file production.${file%.*} | psql -U postgres -d USA_Structures_Buildings >> /tmp/report.txt
	fi
done
