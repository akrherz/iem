<?php
 /* Download .zip files of rainfall estimates! */
include("../../config/settings.inc.php");

$year = isset($_GET["year"]) ? intval($_GET["year"]) : date("Y", time() - 86400);
$month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m", time() - 86400);
$day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d", time() - 86400);
$epsg = isset($_GET["epsg"]) ? intval($_GET["epsg"]) : 4326;
$geometry = isset($_GET["geometry"]) ? $_GET["geometry"] : "point";

$ts = mktime(0,0,0,$month, $day, $year);

chdir("/var/www/htdocs/tmp");
$dir = date("Y/m", $ts);
$fp = sprintf("%s_rain", date("Ymd", $ts));

`cp /mnt/a2/wepp/rainfall/shape/daily/${dir}/${fp}.dbf .`;
`cp /mnt/mesonet/wepp/GIS/static/hrap_${geometry}_${epsg}.shp ${fp}.shp`;
`cp /mnt/mesonet/wepp/GIS/static/hrap_${geometry}_${epsg}.shx ${fp}.shx`;
`cp /mnt/mesonet/data/gis/meta/${epsg}.prj ${fp}.prj`;
`cp /mnt/mesonet/data/gis/avl/iemrainfall.avl ${fp}.avl`;
`zip ${fp}.zip ${fp}*`;
`rm -f ${fp}.dbf ${fp}.shp ${fp}.shx`;

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=${fp}.zip");
readfile("${fp}.zip");


?>
