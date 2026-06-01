<?php
// Prevent client abort from leaving temp files around
ignore_user_abort(true);

require_once "../../../include/throttle.php";
require_once "../../../include/forms.php";
require_once "../../../include/mlib.php";

$dt = dstr2dt(get_str404("dstr"));

$sector = substr(get_str404("sector", "us"), 0, 2);
// Validate sector contains only letters
if (!preg_match('/^[a-zA-Z]+$/', $sector)) {
    http_response_code(422);
    die("Invalid sector format");
}

$tempDir = sys_get_temp_dir() . DIRECTORY_SEPARATOR . uniqid('php_tmp_', true);
mkdir($tempDir, 0700, true);
chdir($tempDir);

$outFile = sprintf("n0q_%s", $dt->format("YmdHi"));
$zipFile = sprintf("n0q_%s.zip", $dt->format("YmdHi"));

$S = strtoupper($sector);
$now = new DateTimeImmutable("now", new DateTimeZone("UTC"));
if ($dt > ($now->sub(new DateInterval('PT6M')))) {
    $inFile = "/mesonet/ldmdata/gis/images/4326/{$S}COMP/n0q_0.tif";
} else {
    $inFile = sprintf("/mesonet/ARCHIVE/data/%s/GIS/{$sector}comp/n0q_%s.png", $dt->format("Y/m/d"), $dt->format("YmdHi"));
}

if (!is_file($inFile)) die("No GIS composite $inFile found for this time!");


$cmd = sprintf("gdalwarp -t_srs %s -s_srs %s -of GTIFF %s %s.tif",
    escapeshellarg("EPSG:4326"),
    escapeshellarg("EPSG:4326"),
    escapeshellarg($inFile),
    escapeshellarg($outFile));
shell_exec($cmd);

$cmd = sprintf("zip %s %s.tif",
    escapeshellarg($zipFile),
    escapeshellarg($outFile));
shell_exec($cmd);

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename={$zipFile}");
readfile($zipFile);

unlink($zipFile);
unlink("{$outFile}.tif");

chdir("..");
shell_exec("rm -rf ". escapeshellarg($tempDir));
