#!/bin/bash
# Test mapserver files

# map2img is mapserver 8, shp2img is mapserver 7
MSEXEC="map2img"
if ! command -v $MSEXEC &> /dev/null
then
    MSEXEC="shp2img"
fi

find . -type f -name '*.map' -print0 | while IFS= read -r -d '' fn; do
    echo "$fn"
    ("$MSEXEC" -o /dev/null -m "$fn" || touch MSFAIL)
done

if [ -e MSFAIL ]; then
    rm -f MSFAIL
    exit 1
fi
