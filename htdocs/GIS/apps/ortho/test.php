<?php
include("../../../../config/settings.inc.php");

dl($mapscript);


$map = ms_newMapObj("test.map");

//$counties = $map->getlayerbyname("counties");
//$counties->set("status", MS_ON);
//$counties->setProjection("proj=latlong");

$ll = $map->getlayerbyname("wmsback");
$ll->set("status", MS_ON);

$site = $map->getlayerbyname("dot");
$site->set("status", MS_ON);

$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);

include("$rootpath/include/station.php");
$st = new StationData($station);
$cities = $st->table;

$projInObj = ms_newprojectionobj("proj=latlong");
$projOutObj = ms_newprojectionobj( $map->getProjection() );

$dPoint = ms_newpointobj();
$dPoint->setXY($cities[$station]['lon'], $cities[$station]['lat']);
$nPoint = $dPoint->project($projInObj, $projOutObj);

$ll_x = $nPoint->x - 750;
$ll_y = $nPoint->y - 750;
$ur_x = $nPoint->x + 750;
$ur_y = $nPoint->y + 750;

$map->setextent($ll_x, $ll_y, $ur_x, $ur_y);

//---
$r0_pt = ms_newpointobj();
$r0_pt->setXY($cities[$station]['lon'] - 0.0050,$cities[$station]['lat'] - 0.0050); 
$r0 = $r0_pt->project($projInObj, $projOutObj);
$r1_pt = ms_newpointobj();
$r1_pt->setXY($cities[$station]['lon'] + 0.0049,$cities[$station]['lat'] + 0.0049); 
$r1 = $r1_pt->project($projInObj, $projOutObj);

//echo $cities[$station]['lon'] ."/". $cities[$station]['lat'] ."<br>";
//echo $r0->x ."/". $r0->y ."/". $r1->x ."/". $r1->y ."<br>";
//echo $nPoint->x ."/". $nPoint->y ;


$img = $map->prepareImage();

$ll->draw($img);

$pt = ms_newPointObj();
$pt->setXY($nPoint->x, $nPoint->y, 0);
$pt->draw($map, $site, $img, 0, "  ". $cities[$station]['name']);
$pt->free();

$rt = ms_newRectObj();
$rt->setextent($r0->x, $r0->y, $r1->x, $r1->y);
$rt->draw($map, $rect, $img, 0, " ");
$rt->free();


//$counties->draw($img);
//$site->draw($img);

$map->drawLabelCache($img);

$url = $img->saveWebImage();
?>

<img src="<?php echo $url; ?>" border="1">
