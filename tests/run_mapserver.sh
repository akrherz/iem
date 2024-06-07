# Test mapserver files

# map2img is mapserver 8, shp2img is mapserver 7
MSEXEC="map2img"
if ! command -v $MSEXEC &> /dev/null
then
    MSEXEC="shp2img"
fi

for fn in $(find . -type f -name '*.map' -print); do
  echo $fn;
  ($MSEXEC -o /dev/null -m $fn || touch MSFAIL);
done

if [ -e MSFAIL ]; then
  rm -f MSFAIL
  exit 1
fi
