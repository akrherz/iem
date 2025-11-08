<?php
// Prevent client abort from leaving temp files around
ignore_user_abort(true);

require_once "../../../include/throttle.php";
require_once "../../../include/forms.php";

date_default_timezone_set('UTC');
putenv("TZ=GMT");
/* This bad boy converts a PNG to a geo-tiff */

$dstr = get_str404("dstr", null);
if (is_null($dstr)) {
    http_response_code(422);
    die("Invalid date format");
}
$sector = substr(get_str404("sector", "us"), 1, 2);
$year = intval(substr($dstr, 0, 4));
$month = intval(substr($dstr, 4, 2));
$day = intval(substr($dstr, 6, 2));
$hour = intval(substr($dstr, 8, 2));
$minute = intval(substr($dstr, 10, 2));
$ts = mktime($hour, $minute, 0, $month, $day, $year);
$now = time();
if ($ts > $now) {
    http_response_code(422);
    die("Request from the future?");
}
$tmpdirname = sys_get_temp_dir() ."/png2gtiff_". bin2hex(random_bytes(8));

mkdir($tmpdirname, 0755);
chdir($tmpdirname);

$outFile = sprintf("n0q_%s", date("YmdHi", $ts));
$zipFile = sprintf("n0q_%s.zip", date("YmdHi", $ts));

$S = strtoupper($sector);
if ($ts > ($now - 360.0)) {
    $inFile = "/mesonet/ldmdata/gis/images/4326/{$S}COMP/n0q_0.tif";
} else {
    $inFile = sprintf("/mesonet/ARCHIVE/data/%s/GIS/{$sector}comp/n0q_%s.png", date("Y/m/d", $ts), date("YmdHi", $ts));
}

if (!is_file($inFile)) die("No GIS composite found for this time!");


$cmd = sprintf("/opt/miniconda3/envs/prod/bin/gdalwarp -t_srs \"EPSG:4326\" -s_srs \"EPSG:4326\" -of GTIFF %s %s.tif", $inFile, $outFile);
exec(escapeshellcmd($cmd));  // skipcq

$cmd = "zip $zipFile {$outFile}.tif";
exec(escapeshellcmd($cmd));  // skipcq

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename={$zipFile}");
readfile($zipFile);

unlink($zipFile);
unlink("{$outFile}.tif");

chdir("..");
rmdir($tmpdirname);
