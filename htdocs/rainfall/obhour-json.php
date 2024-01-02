<?php
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$connect = iemdb("iem");
$mesosite = iemdb("mesosite");

$network = isset($_GET["network"]) ? substr($_GET["network"], 0, 20) : "IA_ASOS";
$tstr = isset($_GET["ts"]) ? $_GET["ts"] : gmdate("YmdHi");
$ts = DateTime::createFromFormat("YmdHi", $tstr, new DateTimeZone(("UTC")));

$networks = "'$network'";
if ($network == "IOWA") {
    $networks = "'IA_ASOS'";
}

$intervals = array(1, 3, 6, 12, 24, 48, 72, 168, 720, "midnight");

$data = array();
$sql = "SELECT id, name from stations WHERE network IN ($networks)";
$rs = pg_exec($mesosite, $sql);
for ($i = 0; $z = pg_fetch_array($rs); $i++) {
    $data[$z["id"]] = array(
        "name" => $z["name"],
        "id" => $z["id"],
        "pmidnight" => 0,
        "p1" => 0,
        "p3" => 0,
        "p6" => 0,
        "p12" => 0,
        "p24" => 0,
        "p48" => 0,
        "p72" => 0,
        "p96" => 0,
    );
}

foreach ($intervals as $key => $interval) {
    if ($interval == "midnight") {
        $ts0 = clone $ts;
        $ts0->setTimezone(new DateTimeZone("America/Chicago"));
        $ts0->setTime(0, 0, 0);
        $ts0->setTimezone(new DateTimeZone("UTC"));
    } else {
        $ts0 = clone $ts;
        $ts0->sub(new DateInterval("PT{$interval}H"));
    }
    // Lame, but is a faster
    $table = sprintf("hourly_%s", $ts0->format("Y"));
    if ($ts0->format("Y") != $ts->format("Y")) {
        $table = "hourly";
    }
    $sql = sprintf(
        "select id as station, sum(phour) as p1 from %s h " .
            "JOIN stations t on (h.iemid = t.iemid) WHERE valid >= '%s+00' and " .
            "valid < '%s+00' and t.network IN (%s) " .
            "GROUP by t.id",
        $table,
        $ts0->format("Y-m-d H:i"),
        $ts->format("Y-m-d H:i"),
        $networks
    );
    $rs = pg_exec($connect, $sql);
    for ($i = 0; $z = pg_fetch_array($rs); $i++) {
        // hackery to account for trace values
        $val = floatval($z["p1"]);
        if ($val > 0.005) {
            $retval = round($val, 2);
        } else if ($val > 0) {
            $retval = 0.0001;
        } else {
            $retval = 0;
        }
        $data[$z["station"]]["p$interval"]  = $retval;
    }
}

$ar = array("precip" => array());
foreach ($data as $station => $d) {
    $ar["precip"][] = $d;
}

echo json_encode($ar);
