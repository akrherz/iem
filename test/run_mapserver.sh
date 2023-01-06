# Test mapserver files
# NOTE shp2img is mapserver 7, update to map2img

for fn in $(find . -type f -name '*.map' -print); do
  echo $fn;
  (shp2img -o /dev/null -m $fn || touch MSFAIL);
done

if [ -e MSFAIL ]; then
  rm -f MSFAIL
  exit 1
fi
