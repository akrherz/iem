<?php
/*
 *  Giveme JSON data listing of webcams 
 */
header('content-type: application/json; charset=utf-8');
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

// This should be a UTC timestamp, gasp!
$ts = isset($_REQUEST["ts"]) ? strtotime($_REQUEST["ts"]) : 0;
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"], 0, 4) : "KCCI";

$connect = iemdb("mesosite");
pg_exec($connect, "SET TIME ZONE 'UTC'");

if ($ts > 0) {
    if ($network != "IDOT") {
        $rs = pg_prepare($connect, "CAMSEL", "SELECT * from " .
            "camera_log c, webcams w WHERE valid = $1 and c.cam = w.id " .
            "and w.network = $2 ORDER by name ASC");

        $ar = array(
            date('Y-m-d H:i', $ts),
            $network
        );
    } else {
        // Timestamps are not exact with the RWIS webcams, so we support a
        // +/- 10 minute offset
        $rs = pg_prepare(
            $connect,
            "CAMSEL",
            "SELECT * from camera_log c, webcams w WHERE " .
                "valid BETWEEN $1 and $2 and c.cam = w.id " .
                "and w.network = $3 ORDER by name ASC, valid ASC"
        );
        $ar = array(
            date('Y-m-d H:i', $ts - (10 * 60)),
            date('Y-m-d H:i', $ts + (10 * 60)),
            $network,
        );
    }
} else {
    $rs = pg_prepare($connect, "CAMSEL", "SELECT * from "
        . "camera_current c, webcams w WHERE "
        . "valid > (now() - '30 minutes'::interval) and c.cam = w.id "
        . "and w.network = $1 ORDER by name ASC");
    $ar = array($network);
}
$result = pg_execute($connect, "CAMSEL", $ar);


$ar = array("images" => array());
if ($ts > 0) {
    $url = "https://mesonet.agron.iastate.edu/current/camrad.php?network=${network}&ts=" . $_REQUEST["ts"];
} else {
    $url = "https://mesonet.agron.iastate.edu/current/camrad.php?network=${network}&" . time();
}
if (pg_num_rows($result) > 0) {
    $ar["images"][] = array(
        "cid" => "${network}-000",
        "name" => " NEXRAD Overview",
        "county" => "",
        "network" => "",
        "state" => "",
        "url" => $url
    );
}
$used = array();
for ($i = 0; $row = pg_fetch_assoc($result); $i++) {
    if (array_key_exists($row["cam"], $used)) {
        continue;
    }
    $used[$row["cam"]] = True;
    $gts = strtotime($row["valid"]);
    $url = sprintf(
        "https://mesonet.agron.iastate.edu/archive/data/%s/camera/%s/%s_%s.jpg",
        gmdate("Y/m/d", $gts),
        $row["cam"],
        $row["cam"],
        gmdate("YmdHi", $gts)
    );
    $z = array(
        "cid" => $row["id"],
        "name" => $row["name"],
        "county" => $row["county"],
        "state" => $row["state"],
        "network" => $row["network"],
        "url" => $url
    );
    $ar["images"][] = $z;
}

$json = json_encode($ar);

# JSON if no callback
if (!isset($_REQUEST['callback']))
    exit($json);

$cb = xssafe($_REQUEST['callback']);
exit("{$cb}($json)");
