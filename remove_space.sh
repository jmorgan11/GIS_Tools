#!/bin/bash
#
for name in *' '*; do
	mv -- "$name" "${name// /_}"
done
