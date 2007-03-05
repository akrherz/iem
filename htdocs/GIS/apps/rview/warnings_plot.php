<?php
include_once("../../../../config/settings.inc.php");
global $_DATABASES;
/**
Variables that need to be set before including this
$isarchive -  is this an archived call?
$imgi - for loop sequence
$tzoff - time zone offset
$interval - minutes between frames
$ts - GMT valid time
$width - image width
$height - image height
$zoom - km zoom extent
$lat0 $lon0 - where shall we center it!
$layers - array of layers to map out
$lsrwindow - how far do we look out
$lsrlook - +/-/0
 */


/* If this is an archive request, or if it is for not current images */
if ($isarchive || ($imgi != 0) )
{
  /* Set us ahead to GMT and then back into the archive */
  $ts = $basets + $tzoff - ($imgi * 60 * $interval );
  $radfile = "/mesonet/ARCHIVE/data/". date('Y/m/d/', $ts) ."GIS/uscomp/n0r_". date('YmdHi', $ts) .".png";
  if (! is_file($radfile)) {
    echo "<br /><i><b>NEXRAD composite not available: $radfile</b></i>";
  } 
} else 
{
  $ts = filemtime("/home/ldm/data/gis/images/4326/USCOMP/n0r_".$imgi.".png") - ($imgi * 300);
  $radfile = "/home/ldm/data/gis/images/4326/USCOMP/n0r_".$imgi.".tif";
}
$myarchive = 0;
if ($imgi >0) $myarchive = 1;

if ($tzoff == 0)
{
  $d = date("d M Y H:i T" ,  $ts);
}
else 
{
  $d = date("d M Y h:i A " ,  $ts - $tzoff) . $tz;
}
//$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts + 5 *3600);
$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts );


$map = ms_newMapObj("$rootpath/data/gis/base4326.map");
$map->set("width", $width);
$map->set("height", $height);


if (isset($x0))
  $map->setextent($x0,$y0,$x1,$y1);
else {
  $lpad = $zoom / 100.0;
  $map->setextent($lon0 - $lpad,
                $lat0 - $lpad,
                $lon0 + $lpad,
                $lat0 + $lpad);
}

$map->setProjection("proj=latlong");

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$GOESBASE = "/home/ldm/data/gis/images/4326/goes";
$goes_east1V = $map->getlayerbyname("goes_east1V");
if (in_array("goes_east1V", $layers)) 
{
  $a = find_sat("east1V", $ts);
  if ($a >= 0)
  {
    $goes_east1V->set("data", "${GOESBASE}/east1V_${a}.tif");
    $goes_east1V->set("status", 1);
  }
}

$goes_west1V = $map->getlayerbyname("goes_west1V");
if (in_array("goes_west1V", $layers))
{
  $a = find_sat("west1V", $ts);
  if ($a >= 0)
  {
    $goes_west1V->set("data", "${GOESBASE}/west1V_${a}.tif");
    $goes_west1V->set("status", 1);
  }
}
$goes_west04I4 = $map->getlayerbyname("goes_west04I4");
if (in_array("goes_west04I4", $layers))
{
  $a = find_sat("west04I4", $ts);
  if ($a >= 0)
  {
    $goes_west04I4->set("data", "${GOESBASE}/west04I4_${a}.tif");
    $goes_west04I4->set("status", 1);
  }
}

$goes_east04I4 = $map->getlayerbyname("goes_east04I4");
if (in_array("goes_east04I4", $layers))
{
  $a = find_sat("east04I4", $ts);
  if ($a >= 0)
  {
    $goes_east04I4->set("data", "${GOESBASE}/east04I4_${a}.tif");
    $goes_east04I4->set("status", 1);
  }
}

$airtemps = $map->getlayerbyname("airtemps");
$airtemps->set("status", (in_array("airtemps", $layers) && ! $myarchive) );
$airtemps->set("connection", $_DATABASES["access"] );

$surface = $map->getlayerbyname("surface");
$surface->set("status", (in_array("surface", $layers) && ! $myarchive) );
$surface->set("connection", $_DATABASES["access"] );

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", 1);

$clayer = $map->getlayerbyname("uscounties");
$clayer->set("status", in_array("uscounties", $layers) );

$cwas = $map->getlayerbyname("cwas");
$cwas->set("status", in_array("cwas", $layers) );

$usdm = $map->getlayerbyname("usdm");
$usdm->set("status", (in_array("usdm", $layers) && ! $myarchive) );

$watches = $map->getlayerbyname("watches");
$watches->set("connection", $_DATABASES["postgis"] );
$watches->set("status", (in_array("watches", $layers)) );
//$watches->setFilter("expired > '".$db_ts."' and issued <= '".$db_ts."'");
$watches->set("data", "geom from (select type as wtype, geom, oid from watches where expired > '".$db_ts."' and issued <= '".$db_ts."') as foo using unique oid using srid=4326");

$c0 = $map->getlayerbyname("warnings0_c");
$c0->set("connection", $_DATABASES["postgis"] );
$c0->set("status", in_array("warnings", $layers) );
if ($isarchive)
{ 
   $c0->set("data", "geom from (select significance, phenomena, geom, oid from warnings_$year WHERE expire > '$db_ts' and issue <= '$db_ts' and gtype = 'C' ORDER by phenomena ASC) as foo using unique oid using SRID=4326");
}else {
   $sql = "geom from (select significance, phenomena, geom, oid from warnings WHERE expire > '$db_ts' and gtype = 'C' ORDER by phenomena ASC) as foo using unique oid using SRID=4326";
   $c0->set("data", $sql);
}
$q = "expire > '".$db_ts."' and issue <= '".$db_ts."' and gtype = 'C'";


//$warnsum = $map->getlayerbyname("warnings_summary");
//$warnsum->set("connection", $_DATABASES["postgis"] );
//$warnsum->set("status", in_array("warnings_summary", $layers) );

/* Polygon Warnings */
$p0 = $map->getlayerbyname("warnings0_p");
$p0->set("connection", $_DATABASES["postgis"] );
$p0->set("status", in_array("warnings", $layers) );
if ($isarchive)
{ 
  $sql = "geom from (select phenomena, geom, oid from warnings_$year WHERE significance != 'A' and expire > '$db_ts' and issue <= '$db_ts' and gtype = 'P') as foo using unique oid using SRID=4326";
  //echo $sql;
  $p0->set("data", $sql);
} else {
 $p0->set("data", "geom from (select phenomena, geom, oid from warnings WHERE significance != 'A' and expire > '$db_ts' and issue <= '$db_ts' and gtype = 'P') as foo using unique oid using SRID=4326");
//$p0->setFilter("significance != 'A' and expire > '".$db_ts."' and issue < '". $db_ts."' and gtype = 'P'");
}
$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("data", $radfile);
$radar->set("status", in_array("nexrad", $layers) );

$lsrs = $map->getlayerbyname("lsrs");
$lsrs->set("connection", $_DATABASES["postgis"] );
$lsrs->set("status", MS_ON);
if ($lsrwindow == 0)
{
  $lsrs->set("status", MS_OFF);
}
$lsr_btime = strftime("%Y-%m-%d %H:%M:00+00", $ts - ($lsrwindow * 60) );
if ($lsrlook == "+") 
   $lsr_btime = strftime("%Y-%m-%d %H:%M:00+00", $ts);
$lsr_etime = strftime("%Y-%m-%d %H:%M:00+00", $ts + ($lsrwindow * 60) );
if ($lsrlook == "-") 
   $lsr_etime = strftime("%Y-%m-%d %H:%M:00+00", $ts);
//$lsrs->setFilter("valid >= '$lsr_btime' and valid <= '$lsr_etime'");
$lsrs->set("data", "geom from (select distinct city, magnitude, valid, geom, type as ltype, city || magnitude || x(geom) || y(geom) as k from lsrs_${year} WHERE valid >= '$lsr_btime' and valid <= '$lsr_etime') as foo USING unique k USING SRID=4326 ");

$img = $map->prepareImage();

$Srect = $map->extent;
$namer->draw($img);
$goes_east1V->draw($img);
$goes_west1V->draw($img);
$goes_east04I4->draw($img);
$goes_west04I4->draw($img);
$clayer->draw( $img );
$stlayer->draw( $img);
$lakes->draw($img);
$radar->draw($img);
$cwas->draw( $img);
$watches->draw($img); 
$c0->draw($img);
//$warnsum->draw($img);
$p0->draw($img);
$usdm->draw($img);
if ($lsrwindow != 0)
  $lsrs->draw($img);

$surface->draw($img);
$airtemps->draw($img);

if (! isset($_GET["iem"])) {
 $map->embedScalebar($img);
 mktitle($map, $img, "                 $maptitle $d");
 $map->drawLabelCache($img);
 mklogolocal($map, $img);
} else {
 tv_logo($map,$img, "    $d");
}

$url = $img->saveWebImage();

//$ltmp = $map->drawLegend();
//$legendsrc = $ltmp->saveWebImage();

//$stmp = $map->drawScaleBar();
//$scalesrc = $stmp->saveWebImage();

?>
