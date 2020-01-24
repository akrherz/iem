<?php
putenv("TZ=GMT");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
$mos = iemdb("mos");
pg_exec($mos, "SET TIME ZONE 'UTC'");


$station = isset($_GET["station"])? $_GET["station"]: "KAMW";
$ts = isset($_GET["valid"])? strtotime($_GET["valid"]): time();
$year = intval(date("Y", $ts));
if ($year < 2007){
	exit();
}

$rs = pg_prepare($mos, "SELECTOR", "select *, t06_1 ||'/'||t06_2 as t06, 
                 t12_1 ||'/'|| t12_2 as t12  from t${year} WHERE station = $1
                 and ftime >= $2 and ftime <= ($2 + '10 days'::interval) ORDER by ftime ASC");


if (isset($_GET["runtime"]) && isset($_GET["model"])){
  $ts = strtotime($_GET["runtime"]);
  $year = intval(date("Y", $ts));
  if ($year < 2007){
  	die("Bad runtime '". $_GET["runtime"]. "'");
  }
  $rs = pg_prepare($mos, "SELECTOR2", "select *, t06_1 ||'/'||t06_2 as t06, 
                 t12_1 ||'/'|| t12_2 as t12  from t${year} WHERE station = $1
                 and runtime = $2 and model = $3 ORDER by ftime ASC");
  $rs = pg_execute($mos, "SELECTOR2", Array($station, date("Y-m-d H:i",$ts),
        $_GET["model"]));
} else {
  $rs = pg_execute($mos, "SELECTOR", Array($station, date("Y-m-d H:i",$ts)));
}

header("Content-type: text/plain");

$ar = Array(
  "station", "model", "runtime", "ftime", "n_x", "tmp", "dpt",
  "cld", "wdr", "wsp", "p06", "p12", "q06", "q12","t06", "t12",
  "snw", "cig", "vis", "obv", "poz", "pos", "typ", "sky", "swh", "lcb",
  "i06", "slv", "s06", "pra", "ppl", "psn", "pzr", "t03", "gst");

echo implode(",", $ar) ."\n";
for ($i=0;$row=pg_fetch_array($rs);$i++)
{
  foreach($ar as $k => $v)
  {
    echo sprintf("%s,", $row[$v]);
  }
  echo "\n";
}
