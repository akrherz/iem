<?php

function mktitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");
                                                                                
  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(10, 15);
                                                                                
  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}
                                                                                
function mklogolocal($map, $imgObj) {
                                                                                
 $layer = $map->getLayerByName("logo");
                                                                                
 // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(44, 24);
                                                                                
 $point->draw($map, $layer, $imgObj, "logo", "");
}

function drawStateNEXRAD($hlext) {
 $width = 350;
 $height = 300;

 $map = ms_newMapObj("mosaic.map");
 $map->set("width", $width);
 $map->set("height", $height);

 $map->setextent(-96.639706, 40.375437,-90.140061, 43.501196);
 $map->setProjection("init=epsg:4326");

 $counties = $map->getlayerbyname("counties_unproj");
 $counties->set("status", MS_ON);

 $radarL = $map->getlayerbyname("radar");
 $radarL->set("status", MS_ON);

 $img = $map->prepareImage();
 $radarL->draw($img);
 $counties->draw($img);

 $rect = $map->getlayerbyname("rect");
 $rect->set("status", MS_ON);

 /** Draw a box for what we are zoomed in on */
 $rt = ms_newRectObj();
 $rt->setextent($hlext[0], $hlext[1], $hlext[2], $hlext[3]);
 $rt->draw($map, $rect, $img, 0, " ");
 

  
 $url = $img->saveWebImage(MS_PNG, 0,0,-1);

 echo "<form name=\"img\" method=\"GET\" action=\"compare.phtml\">";

 echo "<input type=\"hidden\" name=\"ul_x\" value=\"". $map->extent->minx ."\">
<input type=\"hidden\" name=\"ul_y\" value=\"". $map->extent->maxy ."\">
<input type=\"hidden\" name=\"lr_x\" value=\"". $map->extent->maxx ."\">
<input type=\"hidden\" name=\"lr_y\" value=\"". $map->extent->miny ."\">
<input type=\"hidden\" name=\"map_height\" value=\"". $height ."\">
<input type=\"hidden\" name=\"map_width\" value=\"". $width ."\">";
 echo "<input border=1 name=\"map\" type=\"image\" src=\"$url\"></form>";

 return $url;


}

function drawCountyNEXRAD($site, $extents) {
  $width = "150";
  $height = "150";
 
  /** ----------------------- */
  $map = ms_newMapObj("mosaic.map");
  $map->set("width", $width);
  $map->set("height", $height);

  $map->setextent($extents[0],$extents[1], $extents[2],$extents[3] );
  $map->setProjection("init=epsg:4326");

  $counties = $map->getlayerbyname("counties_unproj");
  $counties->set("status", MS_ON);

  $radarL = $map->getlayerbyname("DMX");
  $radarL->set("status", MS_ON);
  $radarL->set("data", "/mesonet/data/gis/images/unproj/". $site ."/n0r_0.png");

  $img = $map->prepareImage();
  $radarL->draw($img);
  $counties->draw($img);
  
  $url = $img->saveWebImage(MS_PNG, 0,0,-1);
  return $url;

}

function drawKCCI($extents) {
  $width = "150";
  $height = "150";
 
  /** ----------------------- */
  $map = ms_newMapObj("mosaic.map");
  $map->set("width", $width);
  $map->set("height", $height);

  $map->setextent($extents[0],$extents[1], $extents[2],$extents[3] );
  $map->setProjection("init=epsg:4326");

  $counties = $map->getlayerbyname("counties_unproj");
  $counties->set("status", MS_ON);

  $radarL = $map->getlayerbyname("KCCI");
  $radarL->set("status", MS_ON);

  $img = $map->prepareImage();
  $radarL->draw($img);
  $counties->draw($img);
  
  $url = $img->saveWebImage(MS_PNG, 0,0,-1);
  return $url;

}


?>
