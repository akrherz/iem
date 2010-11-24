<?php

// radValid process 20020817_0100
$ts = mktime(substr($radValid, 9, 2), substr($radValid, 11, 2), 0 , 
  substr($radValid, 4, 2), substr($radValid, 6, 2), substr($radValid, 0, 4) );

$now = time();
if (($now - $ts) > 1200) {
  $ts = $now + 5*3600;
  echo "<b><font color='#ff0000'>Warning: RADAR data is very old!</font></b><br>";
}

$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts);
if (strlen($site) == 0){
  $site = "DMX";
}

$map = ms_newMapObj("iawarn.map");
$map->setSize($width, $height);

$pad = 1;
$lpad = 0.4;

//$map->setextent($extents[$site][0],$extents[$site][1],$extents[$site][2],$extents[$site][3] );

//$map->setProjection( $projs[$site] );

$green = $map->addColor(0, 255, 0);
$blue = $map->addColor(0, 0, 255);
$black = $map->addColor(0, 0, 0);
$white = $map->addColor(255, 255, 255);

$counties = $map->getlayerbyname("iowa_counties");
$counties->set("status", MS_ON);

$mcounties = $map->getlayerbyname("more_counties");
$mcounties->set("status", MS_ON);

$st_cl = $counties->getClass(0);
$st_cl->setExpression("'".$fips."'");


$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$cwas = $map->getlayerbyname("cwas");
$cwas->set("status", 1);

$c0 = $map->getlayerbyname("warnings0_c");
$c0->set("status", 1);
$c0->setFilter("(expire > '".$db_ts."' and issue < ('".$db_ts."'::timestamp + '5 minutes'::interval) and gtype = 'C')");

$p0 = $map->getlayerbyname("warnings0_p");
$p0->set("status", 1);
$p0->setFilter("(expire > '".$db_ts."' and issue < ('". $db_ts."'::timestamp + '5 minutes'::interval) and gtype = 'P')");

$radar = $map->getlayerbyname("radar");
$radar->set("data", "/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".png");
$radar->set("status", 1);

$ts = filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".png");
$d = date("d F Y h:i A" ,  $ts);

$img = $map->prepareImage();

$Srect = $map->extent;

$stlayer->draw( $img);
$cwas->draw( $img);
$counties->draw($img);
$mcounties->draw($img);
$radar->draw($img);
$c0->draw($img);
$p0->draw($img);

$map->drawLabelCache($img);

$url = $img->saveWebImage(MS_PNG, 0,0,-1);

?>
