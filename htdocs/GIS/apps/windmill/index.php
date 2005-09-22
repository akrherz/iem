<?php
  // index.php
  //   Prototype for building nice looking station plots.

/** Load mapscript so */
dl("php_mapscript.so");

/** Create the map object */
$map = ms_newMapObj("iem.map");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$img = $map->prepareImage();
$states->draw($img);
$counties->draw($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "<img src=\"$url\">";

echo "<br> $url ";
?>

