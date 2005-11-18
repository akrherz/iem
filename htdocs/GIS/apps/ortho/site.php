<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$c = iemdb("mesosite");

// 19 Nov 2002:  Finalize into production!
// 19 Nov 2002:  Allow zooming.
$type = $_GET["type"];
$id = $_GET["station"];
$zoom = isset($_GET["zoom"]) ? $_GET["zoom"] : 1;

if (strlen($id) > 6 || strlen($id) == 0) $id = 'DSM';
if (strlen($type) == 0) $type="doqqs";

dl($mapscript);

$map = ms_newMapObj("test.map");


//$counties = $map->getlayerbyname("counties");
//$counties->set("status", MS_ON);
//$counties->setProjection("proj=latlong");

$ll = $map->getlayerbyname("wmsback");
$ll->set("connection", "http://cairo.gis.iastate.edu/cgi-bin/server.cgi?format=jpeg&wmtver=1.0.0&request=map&servicename=GetMap&layers=".$type );
//$ll->set('connection', 'http://komodo.gis.iastate.edu/server.cgi?format=jpeg&wmtver=1.0.0&request=map&servicename=GetMap&layers='.$type);
$ll->set("status", MS_ON);

$site = $map->getlayerbyname("dot");
$site->set("status", MS_ON);

$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);

include("$rootpath/include/dbloc.php");
$loc = dbloc26915($c, $id);


$incr = 500;
$ll_x = $loc["x"] - (100+($zoom*$incr));
$ll_y = $loc["y"] - (100+($zoom*$incr));
$ur_x = $loc["x"] + (100+($zoom*$incr));
$ur_y = $loc["y"] + (100+($zoom*$incr));

$map->setextent($ll_x, $ll_y, $ur_x, $ur_y);

//---
/**
$r0_pt = ms_newpointobj();
$r0_pt->setXY($loc['y'] - 0.0050,$loc['x'] - 0.0050); 
$r0 = $r0_pt->project($projInObj, $projOutObj);
$r1_pt = ms_newpointobj();
$r1_pt->setXY($loc['y'] + 0.0049,$loc['x'] + 0.0049); 
$r1 = $r1_pt->project($projInObj, $projOutObj);
*/

//echo $cities[$id]['lon'] ."/". $cities[$id]['lat'] ."<br>";
//echo $r0->x ."/". $r0->y ."/". $r1->x ."/". $r1->y ."<br>";
//echo $nPoint->x ."/". $nPoint->y ;


$img = $map->prepareImage();

$ll->draw($img);

$pt = ms_newPointObj();
$pt->setXY($loc["x"], $loc["y"], 0);
$pt->draw($map, $site, $img, 0, "  ");
$pt->free();

/**
$rt = ms_newRectObj();
$rt->setextent($r0->x, $r0->y, $r1->x, $r1->y);
$rt->draw($map, $rect, $img, 0, " ");
$rt->free();
*/

//$counties->draw($img);
//$site->draw($img);

$img2 = $map->drawScaleBar();
$map->drawLabelCache($img);

$url = $img->saveWebImage();
$url2 = $img2->saveWebImage();
?>

<img src="<?php echo $url; ?>" border="1">
<img src="<?php echo $url2; ?>" border="1">

