<?php
/* 
 * Generate a RADAR image with webcams overlain for some *UTC* timestamp!
 */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/cameras.inc.php";
$conn = iemdb("mesosite");

/* First, we need some GET vars */
$network = isset($_GET["network"]) 
           ? substr($_GET["network"],0,4) : die("No \$network Set");
$ts = 0;
if ($network == "KCRG"){ $cameras["KCCI-017"]["network"] = "KCRG"; }

if (isset($_GET["ts"]) && $_GET["ts"] != "0")
{
  $q = strptime($_GET["ts"],'%Y%m%d%H%M');
  $ts = gmmktime( $q["tm_hour"], $q["tm_min"], 0,
                1 + $q["tm_mon"], $q["tm_mday"], 1900 + $q["tm_year"]);
}
/* Now, we need to figure out if we are in realtime or archive mode */
if (time() - $ts < 300){ $ts = 0; }

if ($ts > 0)
{ /* If we are in archive mode and requesting a non 5 minute interval,
     what shall we do? Lets check for entries in the database */
  $sql = sprintf("SELECT * from camera_log WHERE valid = '%s'", 
               strftime("%Y-%m-%d %H:%M", $ts ) );
  $rs = pg_exec($conn,$sql);
  if (pg_numrows($rs) == 0){
    $ts = $ts - (intval(date("i",$ts)) % 5 * 60);
    $sql = sprintf("SELECT * from camera_log WHERE valid = '%s'", 
               strftime("%Y-%m-%d %H:%M", $ts ) );
    $rs = pg_exec($conn,$sql);
  }

  /* Now we compute the RADAR timestamp, yippee */
  $radts = $ts - (intval(date("i",$ts)) % 5 * 60);
} else {
  $sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval)";
  $rs = pg_exec($conn, $sql);
  $radts = time() - 60 - (intval(date("i",time() - 60)) % 5 * 60);
}
if ($ts == 0){ $ts = time(); }

/* Who was online and where did they look?  Hehe */
$cdrct = Array();
for( $i=0; $row = pg_fetch_array($rs); $i++) 
{
    $cdrct[ $row["cam"] ] = $row["drct"];
}

/* Finally we get to map rendering */
$map = ms_newMapObj("../../data/gis/base4326.map");

/* Hard coded extents based on network */
if ($network == "KCCI")
 $map->setExtent(-95.1,40.55,-92.2,43.4);
elseif ($network == "IDOT")
 $map->setExtent(-95.5,39.7,-91.2,44.6);
elseif ($network == "KELO")
 $map->setExtent(-98.8,42.75,-95.9,45.6);
elseif ($network == "KCRG")
 $map->setExtent(-93.0,40.9,-90.1,43.7);
$map->setSize(320,240);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", 1);

$c0 = $map->getlayerbyname("sbw");
$c0->set("status", MS_ON );
$db_ts = gmstrftime("%Y-%m-%d %H:%M+00", $ts );
$year = date("Y", $ts);
$c0->set("data", "geom from " 
	." (select significance, phenomena, geom, random() as oid from sbw_$year "
	." WHERE polygon_end > '$db_ts' and polygon_begin <= '$db_ts' and "
	." issue <= '$db_ts' "
	." and significance = 'W' ORDER by phenomena ASC) as foo " 
	." using unique oid using SRID=4326");

$radar = $map->getlayerbyname("nexrad_n0q");
$radar->set("status", MS_ON );
$fp = "/mesonet/ARCHIVE/data/". gmdate('Y/m/d/', $radts) ."GIS/uscomp/n0r_". gmdate('YmdHi', $radts) .".png";
if (file_exists($fp)){
  	$radar->set("data", $fp);
	$title = "RADAR";
	$y = 10;
} else{
  	$radar->set("status", MS_OFF );
	$title = "RADAR Unavailable\n";
	$y = 20;
}


$cp = ms_newLayerObj($map);
$cp->setProjection("epsg:4326");
$cp->set("type", MS_SHAPE_POINT);
$cp->set("status", MS_ON);
$cp->set("labelcache", MS_ON);
$cl = ms_newClassObj($cp);
$lbl = new labelObj();
$cl->addLabel($lbl);
//$cl->getLabel(0)->set("type", MS_TRUETYPE);
$cl->getLabel(0)->set("size", 10);
$cl->getLabel(0)->set("position", MS_CR);
$cl->getLabel(0)->set("font", "liberation-bold");
$cl->getLabel(0)->set("force", MS_ON);
$cl->getLabel(0)->set("offsetx", 6);
$cl->getLabel(0)->set("offsety", 0);
$cl->getLabel(0)->outlinecolor->setRGB(255, 255, 255);
$cl->getLabel(0)->color->setRGB(0, 0, 0);

$cl2 = ms_newClassObj($cp);
$lbl = new labelObj();
$cl2->addLabel($lbl);
//$cl2->getLabel(0)->set("type", MS_TRUETYPE);
$cl2->getLabel(0)->set("size", "10");
$cl2->getLabel(0)->set("font", "esri34");
$cl2->getLabel(0)->set("position", MS_CC);
$cl2->getLabel(0)->set("force", MS_ON);
$cl2->getLabel(0)->set("partials", MS_ON);
$cl2->getLabel(0)->outlinecolor->setRGB(0, 0, 0);
$cl2->getLabel(0)->color->setRGB(255, 255, 255);


$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
$stlayer->draw( $img);
$radar->draw($img);
$c0->draw($img);

/* Draw Points */
foreach($cdrct as $key => $drct)
{
   if ($cameras[$key]["network"] != $network) continue;
   $lon = $cameras[$key]['lon'];
   $lat = $cameras[$key]['lat'];

   $pt = ms_newPointObj();
   $pt->setXY($lon, $lat, 0);
   $pt->draw($map, $cp, $img, 0, intval( substr($key,5,3) ) );

   if ($cdrct[$key] >= 0 && $network != 'IDOT')
   {
     $pt = ms_newPointObj();
     $pt->setXY($lon, $lat, 0);
     $cl2->getLabel(0)->set("angle",  (0 - $cdrct[$key]) + 90 );
     $pt->draw($map, $cp, $img, 1, 'a' );
   }
}
$d = date("m/d/Y h:i A", $radts);

$layer = $map->getLayerByName("credits");
$point = ms_newpointobj();
$point->setXY(5, $y);
$point->draw($map, $layer, $img, 0,  "${title}: $d");

$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>