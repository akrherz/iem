<?php
require_once "/usr/lib64/php/modules/mapscript.php";

require_once "../../../../config/settings.inc.php";
// -----------------------------------------------------------------
// request.php
//   Give the user the climate data in the format they want...
// -----------------------------------------------------------------

// Prevent client abort from leaving temp files around
ignore_user_abort(true);

require_once "../../../../include/database.inc.php";
require_once "../../../../include/network.php";
require_once "../../../../include/forms.php";
$month = get_int404("month", 1);
$day = get_int404("day", 1);

$ts = new DateTime("2000-{$month}-{$day}");
$sqlDate = $ts->format('Y-m-d');
$filePre = $ts->format('md') . "_coop";

$pgcon = iemdb("coop");
$rs = pg_exec(
    $pgcon,
    "select c.*, ST_X(s.geom) as lon, ST_Y(s.geom) as lat, s.name, ".
    "to_char(c.valid, 'YYYYMMDD') as cvalid from climate c JOIN stations s ".
    "ON (c.station = s.id) WHERE c.valid = '{$sqlDate}' and ".
    "s.network ~* 'CLIMATE'");

pg_close($pgcon);

@mkdir("/tmp/cli2shp", 0755);
chdir("/tmp/cli2shp");

$shpFname =  $filePre;
$shpFile = new shapeFileObj($shpFname, MS_SHAPEFILE_POINT);
$dbfFile = dbase_create($shpFname . ".dbf", array(
    array("SITE", "C", 6),
    array("CRECORD", "N", 5, 0),
    array("DATE", "D"),
    array("AVG_HIGH", "N", 3, 0),
    array("AVG_LOW", "N", 3, 0),
    array("AVG_PREC", "N", 8, 2),
    array("MAX_PREC", "N", 8, 2),
    array("MAX_HIGH", "N", 3, 0),
    array("MAX_LOW", "N", 3, 0),
    array("MIN_HIGH", "N", 3, 0),
    array("MIN_LOW", "N", 3, 0)
));


for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    // Create the shape
    $pt = new pointObj();
    $pt->setXY($row["lon"], $row["lat"], 0);
    $shpFile->addPoint($pt);

    dbase_add_record($dbfFile, array(
        $row["station"],
        $row["years"],
        $row["cvalid"],
        $row["high"],
        $row["low"],
        $row["precip"],
        $row["max_precip"],
        $row["max_high"],
        $row["max_low"],
        $row["min_high"],
        $row["min_low"]
    ));
} // End of for
unset($shpFile);
dbase_close($dbfFile);

// Generate zip file
copy("/opt/iem/data/gis/meta/4326.prj", $filePre . ".prj");
popen("zip {$filePre}.zip {$filePre}.shp {$filePre}.shx {$filePre}.dbf {$filePre}.prj", 'r');

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename={$filePre}.zip");
readfile("{$filePre}.zip");
unlink("{$filePre}.zip");
unlink("{$filePre}.shp");
unlink("{$filePre}.prj");
unlink("{$filePre}.dbf");
unlink("{$filePre}.shx");
