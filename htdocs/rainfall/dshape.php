<?php
/* Download .zip files of rainfall estimates! */
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

$dt = dt_from_cgi_ymd();
$epsg = get_int404("epsg", 4326);
$geometry = get_str404("geometry", "point");
$duration = get_str404("duration", "day");

if ($duration == 'year') {
    $dir = sprintf("/mesonet/wepp/data/rainfall/shape/yearly");
    $fp = sprintf("%s_rain",  $dt->format("Y"));
} else if ($duration == 'month') {
    $dir = sprintf("/mesonet/wepp/data/rainfall/shape/monthly/%s", $dt->format("Y"));
    $fp = sprintf("%s_rain",  $dt->format("Ym"));
} else {
    $dir = sprintf("/mesonet/wepp/data/rainfall/shape/daily/%s", $dt->format("Y/m"));
    $fp = sprintf("%s_rain",  $dt->format("Ymd"));
}
$dbf = sprintf("%s/%s.dbf", $dir, $fp);
if (!file_exists($dbf)) {
    http_response_code(422);
    die("File not found: {$dbf}");
}

chdir("/tmp");
copy($dbf, $fp . ".dbf");
copy("/mesonet/wepp/GIS/static/hrap_{$geometry}_{$epsg}.shp", $fp . ".shp");
copy("/mesonet/wepp/GIS/static/hrap_{$geometry}_{$epsg}.shx", $fp . ".shx");
copy("/opt/iem/data/gis/meta/{$epsg}.prj", $fp . ".prj");
copy("/opt/iem/data/gis/avl/iemrainfall.avl", $fp . ".avl");
shell_exec("zip {$fp}.zip {$fp}*");

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename={$fp}.zip");
readfile("{$fp}.zip");

unlink("{$fp}.shp");
unlink("{$fp}.shx");
unlink("{$fp}.dbf");
unlink("{$fp}.prj");
unlink("{$fp}.avl");
unlink("{$fp}.zip");
