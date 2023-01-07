<?php
 /* Download .zip files of rainfall estimates! */
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

$year = get_int404("year", date("Y", time() - 86400));
$month = get_int404("month", date("m", time() - 86400));
$day = get_int404("day", date("d", time() - 86400));
$epsg = get_int404("epsg", 4326);
$geometry = isset($_GET["geometry"]) ? xssafe($_GET["geometry"]) : "point";
$duration = isset($_GET["duration"]) ? xssafe($_GET["duration"]) : "day";

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
copy("/mesonet/wepp/GIS/static/hrap_{$geometry}_{$epsg}.shp", $fp.".shp");
copy("/mesonet/wepp/GIS/static/hrap_{$geometry}_{$epsg}.shx", $fp.".shx");
copy("/opt/iem/data/gis/meta/{$epsg}.prj", $fp.".prj");
copy("/opt/iem/data/gis/avl/iemrainfall.avl", $fp.".avl");
`zip {$fp}.zip {$fp}*`;


header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename={$fp}.zip");
readfile("{$fp}.zip");

unlink($fp.".shp");
unlink($fp.".shx");
unlink($fp.".dbf");
unlink($fp.".prj");
unlink($fp.".avl");
unlink("{$fp}.zip");
