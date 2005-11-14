<?php
global $_DATABASES;

if ($isarchive)
{
  $ts = $basets + $tzoff - ($imgi * 300);
  $fp = "/mesonet/ARCHIVE/data/". date('Y/m/d/', $ts) ."GIS/uscomp/n0r_". date('YmdHi', $ts) .".png";
  if (! is_file($fp)) 
    echo "<br /><i><b>NEXRAD composite not available: $fp</b></i>";
  else
  {
    if (! is_file("/tmp/". date('YmdHi', $ts) .".png"))
    {
    copy($fp, "/tmp/". date('YmdHi', $ts) .".png");
    copy("/mesonet/ARCHIVE/data/". date('Y/m/d') ."/GIS/uscomp/n0r.tfw", "/tmp/". date('YmdHi', $ts) .".wld");
    }
  }
  $radfile = "/tmp/". date('YmdHi', $ts) .".png";
} else 
{
  $ts = filemtime("/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".png") - ($imgi * 300);
  $radfile = "/mesonet/data/gis/images/unproj/USCOMP/n0r_".$imgi.".tif";
}

if ($tzoff == 0)
{
  $d = date("d F Y H:i T" ,  $ts);
}
else 
{
  $d = date("d F Y h:i A " ,  $ts - $tzoff) . $tz;
}
//$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts + 5 *3600);
$db_ts = strftime("%Y-%m-%d %H:%M:00+00", $ts );
if (strlen($site) == 0){
  $site = "DMX";
}

$map = ms_newMapObj("mosaic.map");
$map->set("width", $width);
$map->set("height", $height);

$lpad = $zoom / 100.0;

if (isset($x0))
  $map->setextent($x0,$y0,$x1,$y1);
else
  $map->setextent($lon0 - $lpad,
                $lat0 - $lpad,
                $lon0 + $lpad,
                $lat0 + $lpad);

$map->setProjection("proj=latlong");

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", 1);

$clayer = $map->getlayerbyname("counties_unproj");
$clayer->set("status", 1);

$cwas = $map->getlayerbyname("cwas");
$cwas->set("status", 1);

$watches = $map->getlayerbyname("watches");
$watches->set("connection", $_DATABASES["postgis"] );
$watches->set("status", 1);
//$watches->setFilter("expired > '".$db_ts."' and issued <= '".$db_ts."'");
$watches->set("data", "geom from (select type as wtype, geom, oid from watches where expired > '".$db_ts."' and issued <= '".$db_ts."') as foo using unique oid using srid=4326");

$c0 = $map->getlayerbyname("warnings0_c");
$c0->set("connection", $_DATABASES["postgis"] );
$c0->set("status", 1);
if ($isarchive)
{ 
  $c0->set("data", "geom from warnings_$year");
}
$c0->setFilter("significance != 'A' and expire > '".$db_ts."' and issue <= '".$db_ts."' and gtype = 'C'");
$q = "expire > '".$db_ts."' and issue <= '".$db_ts."' and gtype = 'C'";

$p0 = $map->getlayerbyname("warnings0_p");
$p0->set("connection", $_DATABASES["postgis"] );
$p0->set("status", 1);
if ($isarchive)
{ 
  $p0->set("data", "geom from warnings_$year");
}
$p0->setFilter("significane != 'A' and expire > '".$db_ts."' and issue < '". $db_ts."' and gtype = 'P'");

$radar = $map->getlayerbyname("radar2");
$radar->set("data", $radfile);
$radar->set("status", 1);

$img = $map->prepareImage();

$Srect = $map->extent;
$namer->draw($img);
$clayer->draw( $img );
$stlayer->draw( $img);
$lakes->draw($img);
$radar->draw($img);
$cwas->draw( $img);
$watches->draw($img); 
$c0->draw($img);
$p0->draw($img);

mktitle($map, $img, "                  IEM NEXRAD composite base reflect valid: $d");
$map->drawLabelCache($img);
mklogolocal($map, $img);

$url = $img->saveWebImage();

?>
