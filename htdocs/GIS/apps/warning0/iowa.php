<?php

dl("php_mapscript_36.so");

$map = ms_newMapObj("warning0.map");

$map->setextent(-247166, -286565, 884179, 588198);

$layer = $map->getlayerbyname(warnings0);
$layer->set("status", 1);

$layer = $map->getlayerbyname(warnings1d);
$layer->set("status", 0);

$layer = $map->getlayerbyname(radar);
$layer->set("status", 1);

$layer = $map->getlayerbyname("counties");
$layer->set("status", 1);

$img = $map->draw();
$url = $img->saveWebImage("MS_PNG", 0,0,-1);
?>

<form method="GET" action="/cgi-bin/mapserv/mapserv">
<input type="hidden" name="mode" value="nquery">
<input type="hidden" name="map" value="/mesonet/www/html/GIS/apps/warning0/warning0.map">
<input type="hidden" name="imgbox" value="-1 -1 -1 -1">
<input type="hidden" name="imgxy" value="224.5 174.5">
<input type="hidden" name="layer" value="warnings0">
<input type="hidden" name="imgext" value="-247166 -286565 884179 588198">


<?php

echo "<input name=\"img\" type=\"image\" src=\"$url\">";

?>

</form>
