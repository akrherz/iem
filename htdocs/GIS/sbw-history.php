<?php
/* Generate an ultra fancy plot of a storm based warning history! */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");
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

$rs = pg_prepare($postgis, "SELECT", "SELECT xmax(geom), ymax(geom), 
        xmin(geom), ymin(geom), *, oid,
        round((area2d(transform(geom,2163))/1000000)::numeric,0 ) as area
        from sbw_$year WHERE phenomena = $1 and 
        eventid = $2 and wfo = $3 and significance = $4
        ORDER by polygon_begin ASC");

$rs = pg_execute($postgis, "SELECT", Array($phenomena, $eventid, $wfo, $significance));

$rows = pg_num_rows($rs);

if ($rows < 2)
{
  $width = 640;
  $height = 540;
  $twidth = 636;
  $theight = 476;
  $px = Array(320,);
  $py = Array(290,);
} else if ($rows >= 2 && $rows < 5)
{
  $width = 640;
  $height = 540;
  $twidth = 316;
  $theight = 236;
  $px = Array(160,480,160,480);
  $py = Array(170,170,410,410);
} else {
  $width = 640;
  $height = 540;
  $twidth = 206;
  $theight = 154;
  $px = Array(110,320,530,110,320,530,110,320,530);
  $py = Array(130,130,130,290,290,290,450,450,450);
}

$map2 = ms_newMapObj($mapFile);
$map2->imagecolor->setrgb(155,155,155);
$map2->set("width", $width);
$map2->set("height",$height);
$img2 = $map2->prepareImage();


$buffer = 0.3;

$oid0 = 0;
$xmax = 0;
$ymax = 0;
$xmin = 0;
$xmax = 0;
for ($i=0;$row = @pg_fetch_array($rs, $i); $i++)
{
  if ($i > 8){ continue; }
  if ($i == 0){
   $oid0 = $row["oid"];
   $xmax = $row["xmax"];
   $ymax = $row["ymax"];
   $xmin = $row["xmin"];
   $ymin = $row["ymin"];
   $xspace = $xmax - $xmin;
   $yspace = ($ymax - $ymin) * 1.5;
   $cross = ($xspace >= $yspace) ? $xspace : $yspace;
   $xc = $xmin + ($xmax - $xmin) / 2;
   $yc = $ymin + ($ymax - $ymin) / 2;
   $xmin = $xc - ($cross / 2) - $buffer;
   $ymin = $yc - ($cross / 2) - (.5 * $buffer);
   $ymax = $yc + ($cross / 2) + (1.5 * $buffer);
   $xmax = $xc + ($cross / 2) + $buffer;
   //echo $xmin ."<br />";
   //echo $xmax ."<br />";
   //echo $ymin ."<br />";
   //echo $ymax ."<br />";
$bar640t = $map2->getLayerByName("bar640t");
$bar640t->set("status", 1);
$bar640t->draw($img2);

$tlayer = $map2->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 12);
if ($rows > 8){
$point->draw($map2, $tlayer, $img2, 0,"Storm Based Warning History (First 9 shown)");
} else{
$point->draw($map2, $tlayer, $img2, 0,"Storm Based Warning History");
}
$point->free();
    
$point = ms_newpointobj();
$point->setXY(80, 29);
$d = strftime("%d %B %Y %-2I:%M %p %Z" ,  strtotime($row["init_expire"]) );
$point->draw($map2, $tlayer, $img2, 1,"$wfo ". $vtec_phenomena[$phenomena] ." ". $vtec_significance[$significance] ." #$eventid till  $d");
$point->free();

$layer = $map2->getLayerByName("logo");
//$lcl0 = $layer->getClass(0);
//$lcl0s0 = $lcl0->getStyle(0);
//$lcl0s0->set("size", 40);
$point = ms_newpointobj();
$point->setXY(40, 26);
$point->draw($map2, $layer, $img2, "logo", "");
$point->free();

$map2->drawLabelCache($img2);

$sz0 = $row["area"];
  }

  $ts = strtotime($row["polygon_begin"]);
  if (time() - $ts > 300)
  { 
    $radts = $ts - (intval(date("i", $ts) % 5) * 60);
  } 

  $map = ms_newMapObj($mapFile);
  $map->set("width", $twidth);
  $map->set("height",$theight);
  $map->setExtent($xmin, $ymin, 
                  $xmax, $ymax);

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
  $wc->setConnectionType( MS_POSTGIS );
  $wc->set("connection", $_DATABASES["postgis"] );
  $wc->set("status", MS_ON );
  $sql = sprintf("geom from (select oid, geom from sbw_$year WHERE oid = ". $oid0 .") as foo using unique oid using SRID=4326");
  $wc->set("data", $sql);
  $wc->set("type", MS_LAYER_LINE);
  $wc->setProjection("init=epsg:4326");

  $wcc0 = ms_newClassObj($wc);
  $wcc0s0 = ms_newStyleObj($wcc0);
  $wcc0s0->color->setRGB(255,255,255);
  $wcc0s0->set("size", 2);
  $wcc0s0->set("symbol", 'circle');
  $wc->draw($img);
  $map->drawLabelCache($img);

  $wc = ms_newLayerObj($map);
  $wc->setConnectionType( MS_POSTGIS );
  $wc->set("connection", $_DATABASES["postgis"] );
  $wc->set("status", MS_ON );
  $sql = sprintf("geom from (select oid, geom from sbw_$year WHERE oid = ". $row["oid"] .") as foo using unique oid using SRID=4326");
  $wc->set("data", $sql);
  $wc->set("type", MS_LAYER_LINE);
  $wc->setProjection("init=epsg:4326");

  $wcc0 = ms_newClassObj($wc);
  $wcc0->set("name", $row["area"] ." sq km [". intval($row["area"]/$sz0 * 100) ."%]" );
  $wcc0s0 = ms_newStyleObj($wcc0);
  $wcc0s0->color->setRGB(255,0,0);
  $wcc0s0->set("size", 3);
  $wcc0s0->set("symbol", 'circle');
  $wc->draw($img);
  $map->drawLabelCache($img);


  $bar640t = $map->getLayerByName("bar640t");
  $bar640t->set("status", 1);
  $bar640t->draw($img);

  $tlayer = $map->getLayerByName("bar640t-title");
  $point = ms_newpointobj();
  $point->setXY(2, 12);
  $point->draw($map, $tlayer, $img, 0, $vtec_status[$row["status"]] );
  $point->free();
    
  $point = ms_newpointobj();
  $point->setXY(2, 29);
  $d = strftime("%d %b %Y %-2I:%M %p %Z" ,  $ts);
  $point->draw($map, $tlayer, $img, 1,"$d");
  $point->free();


  $map->embedLegend($img);
  $map->drawLabelCache($img);


  $img2->pasteImage($img, -1, $px[$i],$py[$i],0);
}
header ("Content-type: image/png");
$img2->saveImage('');
?>
