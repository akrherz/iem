<?php

$ts = mktime(substr($radValid, 9, 2), substr($radValid, 11, 2), 0 , 
  substr($radValid, 4, 2), substr($radValid, 6, 2), substr($radValid, 0, 4) );

$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts);


$map = ms_newMapObj("county.map");

$map->setextent($ll_Point->x - 10000, $ll_Point->y - 10000,
       $ur_Point->x + 10000, $ur_Point->y + 10000);
//$map->setextent($extents[$site][0],$extents[$site][1],
//  $extents[$site][2],$extents[$site][3] );

$map->setProjection( $projs[$site] );

$counties = $map->getlayerbyname("iowa_counties");
$counties->set("status", MS_ON);
$counties->setProjection("init=epsg:4326");

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->setProjection("init=epsg:4326");

$c0 = $map->getlayerbyname("warnings0_c");
$c0->set("status", 1);
$c0->setFilter("(expire > '".$db_ts."' and issue < '".$db_ts."' and gtype = 'C')");

$p0 = $map->getlayerbyname("warnings0_p");
$p0->set("status", 1);
$p0->setFilter("(expire > '".$db_ts."' and issue < '".$db_ts."' and gtype = 'P')");


$radarL = ms_newlayerobj($map);
$radarL->set("status", MS_ON);
$radarL->set("type", MS_LAYER_RASTER );
$radarL->set("data", "/mesonet/data/gis/".$site."_N0R_".$imgi.".tif");
$radarL->set("name", "radarl");
$radarL->setProjection( $projs[$site] );
$radarL->set("offsite", 0);

$img = $map->prepareImage();

$counties->draw($img);
$states->draw($img);
$radarL->draw($img);
$c0->draw($img);
$p0->draw($img);

$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

?>
