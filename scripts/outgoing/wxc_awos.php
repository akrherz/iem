<?php
/*
 * Dump the IEM's processing of Iowa AWOS sites, for a couple of reasons
 * 1) We process the daily precip correctly, whereas WXC does not (last I knew)
 * 2) We get a 5 minute datafed and use it to build more accurate daily totals
 *    not found in the METAR feed.
 */
include "../../config/settings.inc.php";
include "../../include/mlib.php";
include "../../include/network.php";
$nt = new NetworkTable("AWOS");
$cities = $nt->table;

function fancy($v, $floor,$ceil, $p){
  if ($v < $floor || $v > $ceil) return "";
  return sprintf("%${p}.1f", $v);
}

include "../../include/iemaccess.php";
include "../../include/iemaccessob.php";
$iem = new IEMAccess();

$mydata = $iem->getNetwork("AWOS");

$rwis = fopen('/tmp/wxc_ia_awos.txt', 'w');
fwrite($rwis, "Weather Central 001d0300 Surface Data
  13
   5 Station
  52 CityName
   2 State
   7 Lat
   8 Lon
   2 Day
   4 Hour
   5 AirTemp
   5 AirDewp
   4 Wind Direction Degrees
   4 Wind Direction Text
   4 Wind Speed
   5 Today Precipitation
");
 


$now = time();
while ( list($key, $val) = each($mydata) ) {
  $tdiff = $now - $val->db["ts"];
  if ($tdiff > 3600){ continue; }
  if ($val->db['pday'] < 0){ $val->db['pday'] = 0; }

  $s = sprintf("%5s %52s %2s %7s %8s %2s %4s %5s %5s %4s %4s %4s %5s\n", $key, 
    $cities[$key]['name'], 'IA', round($cities[$key]['lat'],2), 
     round($cities[$key]['lon'],2),
     date('d', $val->db['ts'] + (6*3600) ), date('H', $val->db['ts'] + (6*3600)),
     $val->db['tmpf'], $val->db['dwpf'],
     $val->db['drct'], drct2txt($val->db['drct']), $val->db['sknt'], 
     $val->db['pday']); 
  fwrite($rwis, $s);
} // End of while

fclose($rwis);

$pqstr = "data c 000000000000 wxc/wxc_ia_awos.txt bogus txt";
$cmd = sprintf("/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_ia_awos.txt", $pqstr);
system($cmd);
unlink("/tmp/wxc_ia_awos.txt");

?>
