<?php
// Something to generate Mapserver township Stuff
$c = pg_connect("10.10.10.20", 5432, "wepp");
$q = "SELECT xmin(extent) as x0, xmax(extent) as x1,
             ymin(extent) as y0, ymax(extent) as y1 FROM 
        (select extent(the_geom) as extent from iatwp 
         WHERE model_twp = '$twp') as foo";
$rs = pg_exec($c, $q);
$row = pg_fetch_array($rs,0);

if (strlen($height) == 0 || strlen($width) == 0){
  $height = "200";
  $width = "200";
}

dl("php_mapscript.so");
$map = ms_newMapObj("wepp.map");
$map->set("height", $height);
$map->set("width", $width);
$map->setextent($row["x0"] - 1000, $row["y0"], $row["x1"] + 1000, $row["y1"]);

$ll = $map->getlayerbyname("wmsback");
$ll->set("status", MS_ON);

$img = $map->prepareImage();

$ll->draw($img);

$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);

$rt = ms_newRectObj();
$rt->setextent($row["x0"], $row["y0"], $row["x1"], $row["y1"]);
$rt->draw($map, $rect, $img, 0, $twp);
$rt->free();

$map->drawLabelCache($img);


$url = $img->saveWebImage(MS_PNG, 0,0,-1);

?>
<img src="<?php echo $url; ?>" border="1">
