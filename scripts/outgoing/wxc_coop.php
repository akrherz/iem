<?php
/*
 * Generates a Weather Central formatted station datafile with the IEM 
 * processed SHEF (COOP) data included.  Why?  This dataset is difficult
 * to process and I'd like to think I do a great job at it :)
 */

include '../../config/settings.inc.php';
include '../../include/network.php';
$nt = new NetworkTable("IA_COOP");
$cities = $nt->table;

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

include('../../include/iemaccess.php');
include('../../include/iemaccessob.php');

$iem = new IEMAccess();
$net = $iem->getNetwork("IA_COOP");

$now = time();

while (list($key, $iemob) = each($net) ){
    if ((float)$iemob->db["max_tmpf"] < -50) $iemob->db["max_tmpf"] = " ";
    if ((float)$iemob->db["min_tmpf"] > 90) $iemob->db["min_tmpf"] = " ";
    if ((float)$iemob->db["min_tmpf"] < -90) $iemob->db["min_tmpf"] = " ";
    if ((float)$iemob->db["snow"] < 0) $iemob->db["snow"] = " ";
    if ((float)$iemob->db["snow"] < 0) $iemob->db["snow"] = " ";
    if ((float)$iemob->db["snowd"] < 0) $iemob->db["snowd"] = " ";
    if ((float)$iemob->db["pday"] < 0) $iemob->db["pday"] = " ";
    if ($now - $iemob->db["ts"] > 3600*10) continue;   
    $s = sprintf("%5s %-52s %2s %7.4f %9.4f %2s %2s %4s %4s %6s %6s %6s\n",
      $key, $cities[$key]['name'], "IA",
      $cities[$key]['lat'], 
      $cities[$key]['lon'],
      date("d"), "12", $iemob->db["max_tmpf"], $iemob->db["min_tmpf"], 
      $iemob->db["pday"], 
      $iemob->db["snow"], $iemob->db["snowd"] );
    fwrite($coop, $s);
}
fclose($coop);

$pqstr = "data c 000000000000 wxc/wxc_coop.txt bogus txt";
$cmd = sprintf("/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_coop.txt", $pqstr);
system($cmd);
unlink("/tmp/wxc_coop.txt");

?>