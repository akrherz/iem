<?php

function drawRADAR($site, $imgi, $extents, $projs, $radValid, $fips){
  global $_DATABASES;
  global $rootpath;
  include_once("../rview/lib.php");
  $width = "450";
  $height = "450";
  // radValid process 200208170100
  //$ts = mktime(substr($radValid, 8, 2), substr($radValid, 10, 2), 0 , 
  //  substr($radValid, 4, 2), substr($radValid, 6, 2), substr($radValid, 0, 4) );

  $now = time();
  //if (($now - $radValid) > 1200) {
  //  $ts = $now + 5*3600;
  //  echo "<b><font color='#ff0000'>Warning: RADAR data is very old!</font></b><br>";
  //}

  $db_ts = strftime("%Y-%m-%d %H:%M", $radValid);
  if (strlen($site) == 0){
    $site = "DMX";
  }
  $map = ms_newMapObj("$rootpath/data/gis/base4326.map");
  $map->setSize($width, $height);
 

  $map->setextent($extents[$site][0],$extents[$site][1], $extents[$site][2],$extents[$site][3] );

  $namer = $map->getlayerbyname("namerica");
  $namer->set("status", 1);

  $counties = $map->getlayerbyname("uscounties");
  $counties->set("status", MS_ON);

//  $mcounties = $map->getlayerbyname("more_counties");
//  $mcounties->set("status", MS_ON);

//  $st_cl = $counties->getClass(0);
//  $st_cl->setExpression("'".$fips."'");


  $stlayer = $map->getlayerbyname("states");
  $stlayer->set("status", 1);

  $cwas = $map->getlayerbyname("cwas");
  $cwas->set("status", 1);

  $c0 = $map->getlayerbyname("warnings0_c");
  $c0->set("status", 1);
  $c0->set("connection", $_DATABASES["postgis"]);
  $sql = "geom from (select significance, phenomena, geom, oid from warnings WHERE expire > '$db_ts' and issue <= '$db_ts' and gtype = 'C' ORDER by phenomena ASC) as foo using unique oid using SRID=4326";
  $c0->set("data", $sql);

//  $c0->setFilter("(expire > '".$db_ts."' and issue < ('".$db_ts."'::timestamp + '5 minutes'::interval) and gtype = 'C')");

  $p0 = $map->getlayerbyname("warnings0_p");
  $p0->set("connection", $_DATABASES["postgis"]);
  $p0->set("status", 1);
//  $p0->setFilter("(expire > '".$db_ts."' and issue < ('". $db_ts."'::timestamp + '5 minutes'::interval) and gtype = 'P')");
  $p0->set("data", "geom from (select phenomena, geom, oid from warnings WHERE significance != 'A' and expire > '$db_ts' and issue <= '$db_ts' and gtype = 'P') as foo using unique oid using SRID=4326");

  $radarL = $map->getlayerbyname("nexrad_n0r");
  $radarL->set("status", MS_ON);
  $radarL->set("data", "/home/ldm/data/gis/images/4326/". $site ."/n0r_".$imgi.".tif");

  $img = $map->prepareImage();

  $Srect = $map->extent;
  $namer->draw($img);
  $counties->draw($img);
  $stlayer->draw( $img);
  $radarL->draw($img);
  $cwas->draw( $img);
  $p0->draw($img);
  $c0->draw($img);
  $d = date("d F Y H:i T" ,  $radValid);
  mktitle($map, $img, "                  $site valid: $d");
  $map->drawLabelCache($img);
 mklogolocal($map, $img);

  $url = $img->saveWebImage();
  return $url;
}

?>
