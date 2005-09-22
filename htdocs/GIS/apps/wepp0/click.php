<?php
// Hack to figure out where we clicked?

$map_x = $_GET["map_x"];
$map_y = $_GET["map_y"];
$map_height = $_GET["map_height"];
$map_width = $_GET["map_width"];
$ul_x = $_GET["ul_x"];
$ul_y = $_GET["ul_y"];
$lr_x = $_GET["lr_x"];
$lr_y = $_GET["lr_y"];
$year = $_GET["year"];
$month = $_GET["month"];
$day = $_GET["day"];

$dx = ($ul_x - $lr_x) / $map_width;
$dy = ($ul_y - $lr_y) / $map_height;


$clickx = ($map_x * (0 - $dx) ) + $ul_x;
$clicky = ($map_y * (0 - $dy) ) + $ul_y;

$c = pg_connect("10.10.10.20", 5432, "wepp");
$q = "select * from iatwp WHERE truly_inside(geometryfromtext('POINT($clickx $clicky)', 26915), the_geom)";
$rs = pg_exec($c, $q);

$row = @pg_fetch_array($rs, 0);

$twp = $row["model_twp"];

if (strlen($twp) == 0) die("You did not click in Iowa!");

header("Location: township.phtml?twp=$twp&year=$year&month=$month&day=$day");

?>
