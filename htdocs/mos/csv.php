<?php
putenv("TZ=UTC");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";

$station = get_str404("station", "KAMW");
$ts = array_key_exists("valid", $_GET) ? strtotime(xssafe($_GET["valid"])) : time();
$year = intval(date("Y", $ts));
if ($year < 2007) {
    exit();
}

$mos = iemdb("mos");
pg_exec($mos, "SET TIME ZONE 'UTC'");


if (array_key_exists("runtime", $_GET) && array_key_exists("model", $_GET)) {
    $ts = strtotime($_GET["runtime"]);
    $year = intval(date("Y", $ts));
    if ($year < 2007) {
        die("Bad runtime '" . $_GET["runtime"] . "'");
    }
    $stname2 = iem_pg_prepare($mos, "select *, t06_1 ||'/'||t06_2 as t06, 
                 t12_1 ||'/'|| t12_2 as t12  from t{$year} WHERE station = $1
                 and runtime = $2 and model = $3 ORDER by ftime ASC");
    $rs = pg_execute($mos, $stname2, array(
        $station, date("Y-m-d H:i", $ts),
        $_GET["model"]
    ));
} else {
    $stname = iem_pg_prepare($mos, "select *, t06_1 ||'/'||t06_2 as t06, 
    t12_1 ||'/'|| t12_2 as t12 from t{$year} WHERE station = $1
    and ftime >= $2 and ftime <= ($2 + '10 days'::interval) ORDER by ftime ASC");
    $rs = pg_execute($mos, $stname, array($station, date("Y-m-d H:i", $ts)));
}

header("Content-type: text/plain");

$ar = array(
    "station", "model", "runtime", "ftime", "n_x", "tmp", "dpt",
    "cld", "wdr", "wsp", "p06", "p12", "q06", "q12", "t06", "t12",
    "snw", "cig", "vis", "obv", "poz", "pos", "typ", "sky", "swh", "lcb",
    "i06", "slv", "s06", "pra", "ppl", "psn", "pzr", "t03", "gst"
);

echo implode(",", $ar) . "\n";
while ($row = pg_fetch_assoc($rs)) {
    foreach ($ar as $k => $v) {
        echo sprintf("%s,", $row[$v]);
    }
    echo "\n";
}
