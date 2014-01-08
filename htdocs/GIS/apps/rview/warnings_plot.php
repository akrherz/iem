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
$warngeo - to display polygons or not
 */


/* If this is an archive request, or if it is for not current images */
if ($isarchive || ($imgi != 0) )
{
  /* Set us ahead to GMT and then back into the archive */
  $ts = $basets + $tzoff - ($imgi * 60 * $interval );
  $radfile = "/mesonet/ARCHIVE/data/". date('Y/m/d/', $ts) ."GIS/uscomp/n0r_". date('YmdHi', $ts) .".png";
  if (! is_file($radfile)) {
    $content .= "<br /><i><b>NEXRAD composite not available: $radfile</b></i>";
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


$map = ms_newMapObj("../../../../data/gis/base4326.map");
$map->setSize($width,$height);

if (isset($x0))
  $map->setextent($x0,$y0,$x1,$y1);
else {
  $lpad = $zoom / 100.0;
  $map->setextent($lon0 - $lpad,
                $lat0 - $lpad,
                $lon0 + $lpad,
                $lat0 + $lpad);
}


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

$airtemps = $map->getlayerbyname("current_temps");
$airtemps->set("status", (in_array("airtemps", $layers) && ! $isarchive) );
$airtemps->set("connection", $_DATABASES["access"] );

$surface = $map->getlayerbyname("surface");
$surface->set("status", (in_array("surface", $layers) && ! $isarchive) );
$surface->set("connection", $_DATABASES["access"] );

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", 1);

$current_barbs = $map->getlayerbyname("current_barbs");
$current_barbs->set("status", (in_array("current_barbs", $layers) && ! $isarchive ));

$current_sites = $map->getlayerbyname("current_sites");
$current_sites->set("status", (in_array("current_sites", $layers) && ! $isarchive ));

$interstates = $map->getlayerbyname("interstates");
$interstates->set("status", in_array("interstates", $layers));

$clayer = $map->getlayerbyname("uscounties");
$clayer->set("status", in_array("uscounties", $layers) );

$clayer2 = $map->getlayerbyname("uscounties_and_name");
$clayer2->set("status", in_array("uscounties_and_name", $layers) );

$cwas = $map->getlayerbyname("cwas");
$cwas->set("status", in_array("cwas", $layers) );

$usdm = $map->getlayerbyname("usdm");
$usdm->set("status", (in_array("usdm", $layers) && ! $myarchive) );

$watches = $map->getlayerbyname("watches");
$watches->set("connection", $_DATABASES["postgis"] );
$watches->set("status", (in_array("watches", $layers)) );
//$watches->setFilter("expired > '".$db_ts."' and issued <= '".$db_ts."'");
$watches->set("data", "geom from (select type as wtype, geom, "
		." random() as oid from watches where expired > '".$db_ts."' and "
		." issued <= '".$db_ts."') as foo using unique oid using srid=4326");

/* New age custom render only 1 warning! 
 ------------------------------------------------------
*/


if ($warngeo == "both" or $warngeo == "county")
{
    $c0 = $map->getlayerbyname("warnings0_c");
    $c0->set("connection", $_DATABASES["postgis"] );
    $c0->set("status", in_array("warnings", $layers) );
    $c0->set("data", "geom from (select eventid, w.wfo, significance, phenomena, "
  		." u.geom, random() as oid from warnings_$year w JOIN ugcs u "
  		." ON (u.gid = w.gid) WHERE expire > '$db_ts' and issue <= '$db_ts' "
  		." and gtype = 'C' ORDER by phenomena ASC) as foo "
  		." using unique oid using SRID=4326");
}
if ($warngeo == "both")
{
  $p0 = $map->getlayerbyname("warnings0_p");
  $p0->set("connection", $_DATABASES["postgis"] );
  $p0->set("status", in_array("warnings", $layers) );
  $sql = "geom from (select eventid, wfo, significance, phenomena, geom, "
  		." random() as oid from sbw_$year WHERE polygon_end > '$db_ts' "
  		." and polygon_begin <= '$db_ts' and issue <= '$db_ts' "
  		." ) as foo using unique oid using SRID=4326";
  $p0->set("data", $sql);
}
	
if ($warngeo == "sbw")
{
  $p0 = $map->getlayerbyname("sbw");
  $p0->set("connection", $_DATABASES["postgis"] );
  $p0->set("status", in_array("warnings", $layers) );
  $sql = "geom from (select eventid, wfo, significance, phenomena, geom, "
  		." random() as oid from sbw_$year WHERE polygon_end > '$db_ts' "
  		." and polygon_begin <= '$db_ts' and issue < '$db_ts') "
  		." as foo using unique oid using SRID=4326";
  $p0->set("data", $sql);
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
/* Manual over-ride if necessary */
if ( isset($hard_code_lsr_time) ){
  $lsr_btime = strftime("%Y-%m-%d %H:%M:00+00", $lsr_sts);
  $lsr_etime = strftime("%Y-%m-%d %H:%M:00+00", $lsr_ets);
}

$lsrs->set("data", "geom from (select distinct city, magnitude, valid, geom, "
		." type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
		." from lsrs WHERE valid >= '$lsr_btime' and valid <= '$lsr_etime') "
		." as foo USING unique k USING SRID=4326 ");

$img = $map->prepareImage();

$Srect = $map->extent;
$namer->draw($img);
$goes_east1V->draw($img);
$goes_west1V->draw($img);
$goes_east04I4->draw($img);
$goes_west04I4->draw($img);
$clayer->draw( $img );
$clayer2->draw( $img );
$stlayer->draw( $img);
$lakes->draw($img);
$interstates->draw($img);
if (is_file($radfile)){
	$radar->draw($img);
}
$cwas->draw( $img);
$watches->draw($img); 
$current_barbs->draw($img);
$current_sites->draw($img);
$usdm->draw($img);
if ($lsrwindow != 0)
  $lsrs->draw($img);

$surface->draw($img);
$airtemps->draw($img);

  if ($warngeo == "both" or $warngeo == "county"){ $c0->draw($img); }
  if ($warngeo == "both" or $warngeo == "sbw") { $p0->draw($img); }

if (! isset($_GET["iem"])) {
 $map->embedScalebar($img);
 $map->drawLabelCache($img);
 mktitle($map, $img, $maptitle, "Valid: $d", $width);
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
