<?php
/*
 * Generates a Weather Central formatted station datafile with the IEM 
 * processed SHEF (COOP) data included.  Why?  This dataset is difficult
 * to process and I'd like to think I do a great job at it :)
 */

require_once '../../config/settings.inc.php';
require_once '../../include/mlib.php';

$coop = fopen('/tmp/wxc_coop.txt', 'w');
fwrite($coop, "Weather Central 001d0300 Surface Data
  12
   5 Station
  52 CityName
   2 State
   7 Lat
   9 Lon
   2 Day
   2 Hour
   4 24hr High Temp
   4 24hr Low Temp
   6 Precipitation
   6 Snowfall
   6 Snowfall Depth
");
$arr = Array("network" => "IA_COOP");
$jobj = iemws_json("currents.json", $arr);

$now = time();

foreach($jobj["data"] as $bogus => $iemob)
{
    if ((float)$iemob["max_tmpf"] < -50) $iemob["max_tmpf"] = " ";
    if ((float)$iemob["min_tmpf"] > 90) $iemob["min_tmpf"] = " ";
    if ((float)$iemob["min_tmpf"] < -90) $iemob["min_tmpf"] = " ";
    if ((float)$iemob["snow"] < 0) $iemob["snow"] = " ";
    if ((float)$iemob["snow"] < 0) $iemob["snow"] = " ";
    if ((float)$iemob["snowd"] < 0) $iemob["snowd"] = " ";
    if ((float)$iemob["pday"] < 0) $iemob["pday"] = " ";
    if ($now - strtotime($iemob["local_valid"]) > 3600*10) continue;   
    $s = sprintf("%5s %-52s %2s %7.4f %9.4f %2s %2s %4s %4s %6s %6s %6s\n",
      $iemob["station"], $iemob['name'], "IA",
      $iemob['lat'], 
      $iemob['lon'],
      date("d"), "12", $iemob["max_tmpf"], $iemob["min_tmpf"], 
      $iemob["pday"], 
      $iemob["snow"], $iemob["snowd"] );
    fwrite($coop, $s);
}
fclose($coop);

$pqstr = "data c 000000000000 wxc/wxc_coop.txt bogus txt";
$cmd = sprintf("pqinsert -p '%s' /tmp/wxc_coop.txt", $pqstr);
system($cmd);
unlink("/tmp/wxc_coop.txt");

?>