<?php

function determine_time_base($t)
{
  /* Round to the nearest 5 minute! */
  $year = date("Y", $t);
  $month = date("m", $t);
  $day = date("d", $t);
  $hour = date("H", $t);
  $m = intval(date("i", $t) / 5) * 5;
  return mktime($hour, $m, 0, $month, $day, $year);
}

function tv_logo($map, $imgObj, $titlet) 
{
 $layer = $map->getLayerByName("credits");

  // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(80, 400);

 $point->draw($map, $layer, $imgObj, 1, $titlet);
 $map->drawLabelCache($imgObj);

 $layer = $map->getLayerByName("logo");

 $point = ms_newpointobj();
 $point->setXY(80, 400);

 $point->draw($map, $layer, $imgObj, 0, "");



}

function mktitle($map, $imgObj, $titlet, $subtitle="", $width=640) {
	$height = ($subtitle == "")? 36: 53;
	$layer = ms_newLayerObj($map);
	$layer->set("status", MS_ON );
	$layer->set("type", MS_LAYER_POLYGON );
	$layer->set("transform", MS_OFF );
	$wkt = "POLYGON((0 0, 0 $height, $width $height, $width 0, 0 0))";
	$layer->addFeature(ms_shapeObjFromWkt($wkt));

	$layerc0 = ms_newClassObj($layer);
	$layerc0s0 = ms_newStyleObj($layerc0);
	$layerc0s0->color->setRGB(0,0,0);
	$layer->draw($imgObj);
	
	$tlayer = $map->getLayerByName("iem_headerbar_title");
  	$point = ms_newpointobj();
  	$point->setXY(82, 22);
  	$point->draw($map, $tlayer, $imgObj, 0, $titlet);
  	if ($subtitle != ""){
		$point = ms_newpointobj();
		$point->setXY(82, 39);
		$point->draw($map, $tlayer, $imgObj, 1, $subtitle);
  	}
}
                                                                                
function mklogolocal($map, $imgObj) {
                                                                                
 $layer = $map->getLayerByName("logo");
 //$layer->set("transparency", MS_GD_ALPHA);

 // point feature with text for location
 $point = ms_newpointobj();
 $point->setXY(40, 26);
                                                                                
 $point->draw($map, $layer, $imgObj, 0, "");


}

function drawStateNEXRAD($hlext) {
 $width = 350;
 $height = 300;

 $map = ms_newMapObj("mosaic.map");
 $map->set("width", $width);
 $map->set("height", $height);

 $map->setextent(-96.639706, 40.375437,-90.140061, 43.501196);
 $map->setProjection("init=epsg:4326");

 $namerica = $map->getlayerbyname("namerica");
 $namerica->set("status", MS_ON);

 $counties = $map->getlayerbyname("counties_unproj");
 $counties->set("status", MS_ON);

 $radarL = $map->getlayerbyname("radar");
 $radarL->set("status", MS_ON);

 $img = $map->prepareImage();
 $namerica->draw($img);
 $radarL->draw($img);
 $counties->draw($img);

 $rect = $map->getlayerbyname("rect");
 $rect->set("status", MS_ON);

 /** Draw a box for what we are zoomed in on */
 $rt = ms_newRectObj();
 $rt->setextent($hlext[0], $hlext[1], $hlext[2], $hlext[3]);
 $rt->draw($map, $rect, $img, 0, " ");


  
 $url = $img->saveWebImage();

 $s = "<form name=\"img\" method=\"GET\" action=\"compare.phtml\">";

 $s .= "<input type=\"hidden\" name=\"ul_x\" value=\"". $map->extent->minx ."\">
<input type=\"hidden\" name=\"ul_y\" value=\"". $map->extent->maxy ."\">
<input type=\"hidden\" name=\"lr_x\" value=\"". $map->extent->maxx ."\">
<input type=\"hidden\" name=\"lr_y\" value=\"". $map->extent->miny ."\">
<input type=\"hidden\" name=\"map_height\" value=\"". $height ."\">
<input type=\"hidden\" name=\"map_width\" value=\"". $width ."\">";
 $s .= "<input border=1 name=\"map\" type=\"image\" src=\"$url\"></form>";

 return $s;


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

 $namerica = $map->getlayerbyname("namerica");
 $namerica->set("status", MS_ON);
  $counties = $map->getlayerbyname("counties_unproj");
  $counties->set("status", MS_ON);

  $radarL = $map->getlayerbyname("DMX");
  $radarL->set("status", MS_ON);
  $radarL->set("data", "/mesonet/ldmdata/gis/images/4326/ridge/${site}/N0B_0.png");

  $img = $map->prepareImage();
  $namerica->draw($img);
  $radarL->draw($img);
  $counties->draw($img);
  
  $url = $img->saveWebImage();
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

 $namerica = $map->getlayerbyname("namerica");
 $namerica->set("status", MS_ON);
  $counties = $map->getlayerbyname("counties_unproj");
  $counties->set("status", MS_ON);

  $radarL = $map->getlayerbyname("KCCI");
  $radarL->set("status", MS_ON);

  $img = $map->prepareImage();
  $namerica->draw($img);
  $radarL->draw($img);
  $counties->draw($img);
  
  $url = $img->saveWebImage();
  return $url;

}
?>
