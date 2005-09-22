<?php
//  mesoplot/plot.php
//  - Replace GEMPAK mesoplots!!!
$i = isset($_GET["i"]) ? $_GET["i"] : "1h";

$now = time();
$plotts = $now;
if ($i == "1h")
{
	$plotts = mktime( date("H"), 10, 0, date("m"), date("d"), date("Y") );
	if ( date("i", $now) < 10 ){
		$plotts -= 3600;
	}
}

dl("php_mapscript_401.so");

function mktitle($map, $imgObj, $titlet) { 
 
        $layer = $map->getLayerByName("credits");
 
       // point feature with text for location
       $point = ms_newpointobj();
       $point->setXY( 10, 460);

       $point->draw($map, $layer, $imgObj, "credits",
                     $titlet);
}


$map = ms_newMapObj("base.map");



$counties = $map->getlayerbyname("counties");
$counties->set("status", MS_ON);

$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);

if ($i == "1h")
	$temps = $map->getlayerbyname("surface");
else
	$temps = $map->getlayerbyname("surface15m");
$temps->set("status", MS_ON);

$n0r = $map->getlayerbyname("n0r");
$n0r->set("status", MS_ON);




$img = $map->prepareImage();

$states->draw($img);
$n0r->draw($img);
$counties->draw($img);
$temps->draw($img);
$t = date("d M Y h:i A", $plotts);
if ($i == "1h")
mktitle($map, $img, "  1 hour Pressure Change [inches] valid $t");
if ($i == "15m")
mktitle($map, $img, "  Recent 15 minute Pressure Change [inches] valid $t");
$map->drawLabelCache($img);

header("Content-type: image/png");
$img->saveImage('', MS_PNG, 0, 0, -1);
?>
