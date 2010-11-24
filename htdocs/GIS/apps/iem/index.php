<?php
  // index.php
  //   Prototype for building nice looking station plots.



$station = 'SAMI4';
include("../../../include/dbloc.php");
global $loc;
$loc  = dbloc($station);


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


function domap($radius){
  global $loc;
  $map = ms_newMapObj("iem.map");

  $projInObj = ms_newprojectionobj("proj=latlong");
  $projOutObj = ms_newprojectionobj( $map->getProjection() );

  $dPoint = ms_newpointobj();
  $dPoint->setXY($loc['lon'], $loc['lat']);
  $nPoint = $dPoint->project($projInObj, $projOutObj);

  $ll_x = $nPoint->x - ($radius);
  $ll_y = $nPoint->y - ($radius);
  $ur_x = $nPoint->x + ($radius);
  $ur_y = $nPoint->y + ($radius);

  $map->setextent($ll_x, $ll_y, $ur_x, $ur_y);

  $counties = $map->getlayerbyname("counties");
  $counties->set("status", MS_ON);

  $states = $map->getlayerbyname("states");
  $states->set("status", MS_ON);

  $barbs = $map->getlayerbyname("barbs");
  $barbs->set("status", MS_ON);

  $sites = $map->getlayerbyname("sites");
  $sites->set("status", MS_ON);

  $dwpf = $map->getlayerbyname("dwpf");
  $dwpf->set("status", MS_ON);

  $tmpf = $map->getlayerbyname("tmpf");
  $tmpf->set("status", MS_ON);

  $dmx = $map->getlayerbyname("DMX");
  $dmx->set("status", MS_ON);

  $img = $map->prepareImage();
  $states->draw($img);
  $counties->draw($img);
  $dmx->draw($img);
  $sites->draw($img);
  $barbs->draw($img);
  $tmpf->draw($img);
  $dwpf->draw($img);
  $tmpf->draw($img);

  copyright($map, $img, "Current SchoolNet Mesonet");

  $map->drawLabelCache($img);

  $url = $img->saveWebImage(MS_PNG, 0,0,-1);

  echo "Zoom Level: $radius meters<br>";

  echo "<img src=\"$url\">";

  echo "<hr>";
}

domap(5000);
domap(15000);
domap(25000);
domap(50000);
domap(100000);

?>

