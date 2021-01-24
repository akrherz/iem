<?php
 /* Download .zip files of rainfall estimates! */
require_once "../../config/settings.inc.php";

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

$year = isset($_GET["year"]) ? intval($_GET["year"]) : date("Y", time() - 86400);
$month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m", time() - 86400);
$day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d", time() - 86400);
$epsg = isset($_GET["epsg"]) ? intval($_GET["epsg"]) : 4326;
$geometry = isset($_GET["geometry"]) ? $_GET["geometry"] : "point";
$duration = isset($_GET["duration"]) ? $_GET["duration"] : "day";

$ts = mktime(0,0,0,$month, $day, $year);

if ($duration == 'year')
{
  $dir = sprintf("/mesonet/wepp/data/rainfall/shape/yearly");
  $fp = sprintf("%s_rain",  date("Y", $ts) );
}
else if ($duration == 'month')
{
  $dir = sprintf("/mesonet/wepp/data/rainfall/shape/monthly/%s", date("Y", $ts) );
  $fp = sprintf("%s_rain",  date("Ym", $ts) );
}
else
{
  $dir = sprintf("/mesonet/wepp/data/rainfall/shape/daily/%s", date("Y/m", $ts));
  $fp = sprintf("%s_rain",  date("Ymd", $ts) );
}

chdir("/tmp");
copy($dir."/".$fp.".dbf", $fp.".dbf");
copy("/mesonet/wepp/GIS/static/hrap_${geometry}_${epsg}.shp", $fp.".shp");
copy("/mesonet/wepp/GIS/static/hrap_${geometry}_${epsg}.shx", $fp.".shx");
copy("/opt/iem/data/gis/meta/${epsg}.prj", $fp.".prj");
copy("/opt/iem/data/gis/avl/iemrainfall.avl", $fp.".avl");
`zip ${fp}.zip ${fp}*`;


header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=${fp}.zip");
readfile("${fp}.zip");

unlink($fp.".shp");
unlink($fp.".shx");
unlink($fp.".dbf");
unlink($fp.".prj");
unlink($fp.".avl");
unlink("${fp}.zip");
?>
