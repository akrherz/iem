<?php
function mktitlelocal($map, $imgObj, $height, $titlet) { 
 
  $layer = $map->getLayerByName("credits");
  $point = ms_newpointobj();
  $point->setXY( 40, 16);
  $point->draw($map, $layer, $imgObj, 0,
    $titlet ."                                                           ");
  $point->free();

  $point = ms_newpointobj();
  $point->setXY( 0, $height);
  $point->draw($map, $layer, $imgObj, 1,
    "  Iowa Environmental Mesonet | Iowa State Ag Climate Network ");
  $point->free();


}

function plotNoData($map, $img){
  $layer = $map->getLayerByName("credits");

  $point = ms_newpointobj();
  $point->setXY( 100, 200);
  $point->draw($map, $layer, $img, 1,
    "  No data found for this date! ");
  $point->free();

}


?>
