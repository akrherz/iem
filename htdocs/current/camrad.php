<?php
/* Require PHP5 
   Generate a radar image with camera locs for some time 
   17 Apr 2008 - Now we are directly callable!  Yippee 
*/
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/cameras.inc.php");
$conn = iemdb("mesosite");

/* First, we need some GET vars */
$network = isset($_GET["network"]) 
           ? substr($_GET["network"],0,4) : die("No \$network Set");
$ts = 0;
if ($network == "KCRG"){ $cameras["KCCI-017"]["network"] = "KCRG"; }
if (isset($_GET["ts"]))
{
  $q = strptime($_GET["ts"],'%Y%m%d%H%M');
  $ts = mktime( $q["tm_hour"], $q["tm_min"], 0,
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
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
{  $cdrct[ $row["cam"] ] = $row["drct"]; }


/* Finally we get to map rendering */
dl($mapscript);

$map = ms_newMapObj("$rootpath/data/gis/base4326.map");

/* Hard coded extents based on network */
if ($network == "KCCI")
 $map->setExtent(-95.0,40.45,-92.1,43.3);
elseif ($network == "KELO")
 $map->setExtent(-98.0,42.45,-95.1,45.3);
elseif ($network == "KCRG")
 $map->setExtent(-93.0,40.8,-90.1,43.6);

$map->set("width", 320);
$map->set("height", 240);

$namer = $map->getlayerbyname("namerica");
$namer->set("status", 1);

$stlayer = $map->getlayerbyname("states");
$stlayer->set("status", 1);

$counties = $map->getlayerbyname("uscounties");
$counties->set("status", 1);

$c0 = $map->getlayerbyname("sbw");
$c0->set("connection", $_DATABASES["postgis"] );
$c0->set("status", MS_ON );
$db_ts = strftime("%Y-%m-%d %H:%M", $ts );
$year = date("Y", $ts);
$c0->set("data", "geom from (select significance, phenomena, geom, oid from warnings_$year WHERE expire > '$db_ts' and issue <= '$db_ts' and gtype = 'P' and significance = 'W' ORDER by phenomena ASC) as foo using unique oid using SRID=4326");

$radar = $map->getlayerbyname("nexrad_n0r");
$radar->set("status", MS_ON );
if ($ts > 0) 
{
  $fp = "/mnt/a1/ARCHIVE/data/". gmdate('Y/m/d/', $radts) ."GIS/uscomp/n0r_". gmdate('YmdHi', $radts) .".png";
  $radar->set("data", $fp);
}


$cp = ms_newLayerObj($map);
$cp->set("type", MS_SHAPE_POINT);
$cp->set("status", MS_ON);
$cp->set("labelcache", MS_OFF);
$cl = ms_newClassObj($cp);
$cl->label->set("type", MS_BITMAP);
$cl->label->set("size", MS_MEDIUM);
$cl->label->set("position", MS_CR);
$cl->label->set("force", MS_ON);
$cl->label->set("offsetx", 6);
$cl->label->set("offsety", 0);
$cl->label->outlinecolor->setRGB(255, 255, 255);

$cl2 = ms_newClassObj($cp);
$cl2->label->set("type", MS_TRUETYPE);
$cl2->label->set("size", "10");
$cl2->label->set("font", "esri34");
$cl2->label->set("position", MS_CC);
$cl2->label->set("force", MS_ON);
$cl2->label->set("partials", MS_ON);
$cl2->label->outlinecolor->setRGB(0, 0, 0);
$cl2->label->color->setRGB(255, 255, 255);

//$sl = ms_newStyleObj($cl);
//$sl->set("symbolname", "arrow");
//$sl->set("size", 8);
//$sl->color->setRGB(255, 255, 255);
//$sl = ms_newStyleObj($cl);
//$sl->set("symbolname", "circle");
//$sl->set("size", 6);
//$sl->color->setRGB(0, 0, 0);


$img = $map->prepareImage();
$namer->draw($img);
$counties->draw($img);
$stlayer->draw( $img);
$radar->draw($img);
$c0->draw($img);

/* Draw Points */
while (list($key, $drct) = each($cdrct))
{
   if ($cameras[$key]["network"] != $network) continue;
   $lon = $cameras[$key]['lon'];
   $lat = $cameras[$key]['lat'];

   $pt = ms_newPointObj();
   $pt->setXY($lon, $lat, 0);
   $pt->draw($map, $cp, $img, 0, intval( substr($key,5,3) ) );
   $pt->free();

   if ($cdrct[$key] >= 0)
   {
     $pt = ms_newPointObj();
     $pt->setXY($lon, $lat, 0);
     $cl2->label->set("angle",  (0 - $cdrct[$key]) + 90 );
     $pt->draw($map, $cp, $img, 1, 'a' );
     $pt->free();
   }
}
$d = date("m/d/Y h:i A", $radts);

$layer = $map->getLayerByName("credits");
$point = ms_newpointobj();
$point->setXY(125, 10);
$point->draw($map, $layer, $img, "credits",  "RADAR: $d");

$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('');
?>
