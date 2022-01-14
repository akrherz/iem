<?php
putenv("TZ=GMT");
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$mos = iemdb("mos");
pg_exec($mos, "SET TIME ZONE 'UTC'");

$year1 = get_int404("year1", date("Y", time() + 86400));
$year2 = get_int404("year2", date("Y", time() + 86400));
$month1 = get_int404("month1", date("m", time() + 86400));
$month2 = get_int404("month2", date("m", time() + 86400));
$day1 = get_int404("day1", date("d", time() + 86400));
$day2 = get_int404("day2", date("d", time() + 86400));
$hour1 = get_int404("hour1", 0);
$hour2 = get_int404("hour2", 12);

$model = isset($_GET["model"]) ? $_GET["model"]: "GFS";
$station = isset($_GET["station"]) ? strtoupper($_GET["station"]): "KAMW";
$sts = mktime($hour1, 0, 0, $month1, $day1, $year1);
$ets = mktime($hour2, 0, 0, $month2, $day2, $year2);

$table = "alldata";
if ($year1 == $year2) $table = sprintf("t%s", $year1);

$rs = pg_prepare($mos, "SELECTOR", "select *, t06_1 ||'/'||t06_2 as t06, 
                 t12_1 ||'/'|| t12_2 as t12  from $table WHERE station = $1
                 and runtime >= $2 and runtime <= $3 and 
                 (model = $4 or model = $5)
                 ORDER by runtime,ftime ASC");

$model2 = "";
if ($model == "NAM"){ $model2 = "ETA"; }
if ($model == "GFS"){ $model2 = "AVN"; }
$rs = pg_execute($mos, "SELECTOR", Array($station, date("Y-m-d H:i",$sts),
      date("Y-m-d H:i",$ets), $model, $model2 ));

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=mosdata.csv");


$ar = Array(
  "station", "model", "runtime", "ftime", "n_x", "tmp", "dpt",
  "cld", "wdr", "wsp", "p06", "p12", "q06", "q12","t06", "t12",
  "snw", "cig", "vis", "obv", "poz", "pos", "typ", "sky", "swh", "lcb",
  "i06", "slv", "s06", "pra", "ppl", "psn", "pzr", "t03", "gst");

echo implode(",", $ar) ."\n";
for ($i=0;$row=pg_fetch_array($rs);$i++)
{
  reset($ar);
  foreach($ar as $k => $v)
  {
    echo sprintf("%s,", $row[$v]);
  }
  echo "\n";
}
