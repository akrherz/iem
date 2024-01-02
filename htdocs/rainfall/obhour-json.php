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
$sql = <<<EOM
    select id as station,
    sum(case when valid >= '%s' then phour else 0 end) as p1,
    sum(case when valid >= '%s' then phour else 0 end) as p3,
    sum(case when valid >= '%s' then phour else 0 end) as p6,
    sum(case when valid >= '%s' then phour else 0 end) as p12,
    sum(case when valid >= '%s' then phour else 0 end) as p24,
    sum(case when valid >= '%s' then phour else 0 end) as p48,
    sum(case when valid >= '%s' then phour else 0 end) as p72,
    sum(case when valid >= '%s' then phour else 0 end) as p168,
    sum(case when valid >= '%s' then phour else 0 end) as p720,
    sum(case when valid >= '%s' then phour else 0 end) as p2160,
    sum(case when valid >= '%s' then phour else 0 end) as p8760,
    sum(case when valid >= '%s' then phour else 0 end) as pmidnight
    from hourly h
    JOIN stations t on (h.iemid = t.iemid) WHERE
    valid >= '%s' and valid < '%s' and t.network IN (%s)
    GROUP by t.id
EOM;
$sql = sprintf($sql,
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
    $networks
);
$rs = pg_exec($connect, $sql);
for ($i = 0; $z = pg_fetch_array($rs); $i++) {
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

echo json_encode($ar);
