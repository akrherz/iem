<?php
  // index.php
  //   Prototype for building nice looking station plots.



// add copyright
function copyright($map, $imgObj, $titlet) { 
 
 	$layer = $map->getLayerByName("credits");
 
       // point feature with text for location
       $point = ms_newpointobj();
       $point->setXY($map->width - 150, 
                     $map->height - 10);

       $point->draw($map, $layer, $imgObj, "credits",
                     $titlet);
}


$map = ms_newMapObj("test.map");

$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

$sites = $map->getlayerbyname("sites");
$sites->set("status", MS_ON);

$img = $map->prepareImage();
$states->draw($img);
$counties->draw($img);
$sites->draw($img);

copyright($map, $img, "Current SchoolNet Mesonet");

$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

echo "Zoom Level: $radius meters<br>";

echo "<img src=\"$url\">";

echo "<hr>";

?>

