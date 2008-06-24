<?php
/* Generate an ultra fancy plot of a storm based warning history! */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
dl($mapscript);
$mapFile = $rootpath."/data/gis/base4326.map";
$postgis = iemdb("postgis");

/* Figure out what our VTEC is! */
$vtec = isset($_GET["vtec"]) ? $_GET["vtec"]: '2008.KICT.SV.W.0345';

list($year, $wfo, $phenomena, $significance, $eventid) = explode(".", $vtec);
$eventid = intval($eventid);
$year = intval($year);
$wfo = substr($wfo,1,3);
$significance = substr($significance,0,1);

$sql = "SELECT xmax(geom), ymax(geom), xmin(geom), ymin(geom), *, oid
        from sbw_$year WHERE phenomena = '$phenomena' and 
        eventid = $eventid and wfo = '$wfo' and significance = '$significance'
        ORDER by polygon_begin ASC";
$rs = pg_query($postgis, $sql);

$px = Array(160,480,160,480);
$py = Array(120,120,360,360);

$map2 = ms_newMapObj($mapFile);
$map2->set("width", 640);
$map2->set("height",480);
$img2 = $map2->prepareImage();
$buffer = 0.2;

for ($i=0;$row = @pg_fetch_array($rs, $i); $i++)
{
  $ts = strtotime($row["polygon_begin"]);
  if (time() - $ts > 300)
  { 
    $radts = $ts - (intval(date("i", $ts) % 5) * 60);
  } 

  $map = ms_newMapObj($mapFile);
  $map->set("width", 320);
  $map->set("height",240);
  $map->setExtent($row["xmin"] - $buffer, $row["ymin"] - $buffer, 
                  $row["xmax"] + $buffer, $row["ymax"] + $buffer);

  $img = $map->prepareImage();

  $namerica = $map->getlayerbyname("namerica");
  $namerica->set("status", MS_ON);
  $namerica->draw($img);

  $lakes = $map->getlayerbyname("lakes");
  $lakes->set("status", MS_ON);
  $lakes->draw($img);

  /* Draw NEXRAD Layer */
  $radar = $map->getlayerbyname("nexrad_n0r");
  $radar->set("status", MS_ON);
  if (($ts + 300) < time()) {
   $radar->set("data", gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png", $radts) );
  }
  $radar->draw($img);

  $counties = $map->getlayerbyname("uscounties");
  $counties->set("status", MS_ON);
  $counties->draw($img);

  $states = $map->getlayerbyname("states");
  $states->set("status", MS_ON);
  $states->draw($img);


  $wc = ms_newLayerObj($map);
  $wc->set("connectiontype", MS_POSTGIS);
  $wc->set("connection", "user=nobody dbname=postgis host=iemdb");
  $wc->set("status", MS_ON );
  $sql = sprintf("geom from (select oid, geom from sbw_$year WHERE oid = ". $row["oid"] .") as foo using unique oid using SRID=4326");
  $wc->set("data", $sql);
  $wc->set("type", MS_LAYER_LINE);
  $wc->setProjection("init=epsg:4326");

  $wcc0 = ms_newClassObj($wc);
  $wcc0->set("name", "Product");
  $wcc0s0 = ms_newStyleObj($wcc0);
  $wcc0s0->color->setRGB(255,0,0);
  $wcc0s0->set("size", 3);
  $wcc0s0->set("symbol", 1);
  $wc->draw($img);

  $bar640t = $map->getLayerByName("bar640t");
  $bar640t->set("status", 1);
  $bar640t->draw($img);

  $tlayer = $map->getLayerByName("bar640t-title");
  $point = ms_newpointobj();
  $point->setXY(80, 12);
  $point->draw($map, $tlayer, $img, 0,"NEXRAD Base Reflectivity");
  $point->free();
    
  $point = ms_newpointobj();
  $point->setXY(80, 29);
  $d = strftime("%d %B %Y %-2I:%M %p %Z" ,  $ts);
  $point->draw($map, $tlayer, $img, 1,"$d");
  $point->free();

  $map->embedLegend($img);
  $map->drawLabelCache($img);


  $img2->pasteImage($img, '0x0000000', $px[$i],$py[$i],0);
}
header ("Content-type: image/png");
$img2->saveImage('');
?>
