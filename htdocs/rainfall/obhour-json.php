<?php
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$iem = iemdb("iem");
$mesosite = iemdb("mesosite");

$network = isset($_GET["network"]) ? substr($_GET["network"], 0, 20) : "IA_ASOS";
$tstr = isset($_GET["ts"]) ? $_GET["ts"] : gmdate("YmdHi");
$ts = DateTime::createFromFormat("YmdHi", $tstr, new DateTimeZone(("UTC")));

$data = array();
$stname = uniqid("select");
$res = pg_prepare($mesosite, $stname, 
    "SELECT id, name from stations WHERE network = $1");
$rs = pg_execute($mesosite, $stname, array($network));
while ($z = pg_fetch_assoc($rs)) {
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
        "p168" => 0,
        "p720" => 0,
        "p2160" => 0,
        "p8760" => 0,
    );
}

$intervals = array(1, 3, 6, 12, 24, 48, 72, 168, 720, 2160, 8760, "midnight");
$tstamps = array();
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
    $tstamps[$interval] = $ts0->format("Y-m-d H:i") . "+00";
}
$stname = uniqid("select");
$rs = pg_prepare($iem, $stname, <<<EOM
    select id as station,
    sum(case when valid >= $1 then phour else 0 end) as p1,
    sum(case when valid >= $2 then phour else 0 end) as p3,
    sum(case when valid >= $3 then phour else 0 end) as p6,
    sum(case when valid >= $4 then phour else 0 end) as p12,
    sum(case when valid >= $5 then phour else 0 end) as p24,
    sum(case when valid >= $6 then phour else 0 end) as p48,
    sum(case when valid >= $7 then phour else 0 end) as p72,
    sum(case when valid >= $8 then phour else 0 end) as p168,
    sum(case when valid >= $9 then phour else 0 end) as p720,
    sum(case when valid >= $10 then phour else 0 end) as p2160,
    sum(case when valid >= $11 then phour else 0 end) as p8760,
    sum(case when valid >= $12 then phour else 0 end) as pmidnight
    from hourly h
    JOIN stations t on (h.iemid = t.iemid) WHERE
    valid >= $13 and valid < $14 and t.network = $15
    GROUP by t.id
EOM);
$rs = pg_execute($iem, $stname, array(
    $tstamps[1],
    $tstamps[3],
    $tstamps[6],
    $tstamps[12],
    $tstamps[24],
    $tstamps[48],
    $tstamps[72],
    $tstamps[168],
    $tstamps[720],
    $tstamps[2160],
    $tstamps[8760],
    $tstamps["midnight"],
    $tstamps[8760],
    $ts->format("Y-m-d H:i") ."+00",
    $network)
);
while ($z = pg_fetch_assoc($rs)) {
    foreach ($intervals as $key => $interval) {
        // hackery to account for trace values
        $val = floatval($z["p$interval"]);
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

header('Content-type: application/json');
echo json_encode($ar);
