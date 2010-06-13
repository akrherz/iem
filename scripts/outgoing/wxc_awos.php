<?php
include("../../config/settings.inc.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/currentOb.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("AWOS");
$cities = $nt->table;

function fancy($v, $floor,$ceil, $p){
  if ($v < $floor || $v > $ceil) return "";
  return sprintf("%${p}.1f", $v);
}

include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
$iem = new IEMAccess();

$mydata = $iem->getNetwork("AWOS");

$rwis = fopen('wxc_ia_awos.txt', 'w');
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

`/home/ldm/bin/pqinsert wxc_ia_awos.txt >& /dev/null`;
`mv wxc_ia_awos.txt /mesonet/share/pickup/wxc/`;

?>
