<?php
include("../../config/settings.inc.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/currentOb.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;

function fancy($v, $floor,$ceil, $p){
  if ($v < $floor || $v > $ceil) return "";
  return sprintf("%${p}.1f", $v);
}

include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
$iem = new IEMAccess();

$mydata = $iem->getNetwork("IA_RWIS");

$rwis = fopen('wxc_iadot.txt', 'w');
fwrite($rwis, "Weather Central 001d0300 Surface Data
  18
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
   4 SubSurface Temp
   4 P1 Temp
   4 P2 Temp
   4 P3 Temp
   4 P4 Temp
   4 Pave Ave Temp
");
 


$now = time();
while ( list($key, $val) = each($mydata) ) {
  $tdiff = $now - $val->db["ts"];

  if ($val->db['tsf0'] == "") $val->db['tsf0'] = -99.99;
  if ($val->db['tsf1'] == "") $val->db['tsf1'] = -99.99;
  if ($val->db['tsf2'] == "") $val->db['tsf2'] = -99.99;
  if ($val->db['tsf3'] == "") $val->db['tsf3'] = -99.99;
  $t = Array($val->db['tsf0'], $val->db['tsf1'],
     $val->db['tsf2'], $val->db['tsf3']);
  arsort($t);
  //print_r($t);
  while (min($t) < -39.99){
    $ba = array_pop($t);
    if (sizeof($t) == 0) break;
  }
  asort($t);
  if (sizeof($t) > 0){
    while ((max($t) - min($t)) > 20){ $ba = array_pop($t); }
    $val->db['pave_avg'] = array_sum($t) / sizeof($t);
  } else {
    $val->db['pave_avg'] = -99.99;
  }
  //echo  $val->db['pave_avg'];



  if ($tdiff < 1800){
  if (round($val->db['rwis_subf'],0) == -100) $val->db['rwis_subf'] = 'M';
  else $val->db['rwis_subf'] = round($val->db['rwis_subf'],0);
  if (round($val->db['tsf0'],0) == -100) $val->db['tsf0'] = 'M';
  else $val->db['tsf0'] = round($val->db['tsf0'],0);
  if (round($val->db['tsf1'],0) == -100) $val->db['tsf1'] = 'M';
  else $val->db['tsf1'] = round($val->db['tsf1'],0);
  if (round($val->db['tsf2'],0) == -100) $val->db['tsf2'] = 'M';
  else $val->db['tsf2'] = round($val->db['tsf2'],0);
  if (round($val->db['tsf3'],0) == -100) $val->db['tsf3'] = 'M';
  else $val->db['tsf3'] = round($val->db['tsf3'],0);
  if (round($val->db['pave_avg'],0) == -100) $val->db['pave_avg'] = 'M';
  else $val->db['pave_avg'] = round($val->db['pave_avg'],0);

  $s = sprintf("%5s %52s %2s %7s %8s %2s %4s %5s %5s %4s %4s %4s %4s %4s %4s %4s %4s %4s\n", $key, 
    $cities[$key]['name'], 'IA', round($cities[$key]['lat'],2), 
     round($cities[$key]['lon'],2),
     date('d', $val->db['ts'] + (6*3600) ), date('H', $val->db['ts'] + (6*3600)),
     $val->db['tmpf'], $val->db['dwpf'],
     $val->db['drct'], drct2txt($val->db['drct']), $val->db['sknt'], 
     $val->db['rwis_subf'],
     $val->db['tsf0'], $val->db['tsf1'], 
     $val->db['tsf2'], $val->db['tsf3'],
     $val->db['pave_avg'] ); 
  fwrite($rwis, $s);
  }
} // End of while

fclose($rwis);

`/home/ldm/bin/pqinsert wxc_iadot.txt >& /dev/null`;
`mv wxc_iadot.txt /mesonet/share/pickup/wxc/`;

$nt->table = Array();
$nt->load_network("IL_RWIS");
$cities = $nt->table;

$mydata = $iem->getNetwork("IL_RWIS");

$rwis = fopen('wxc_ildot.txt', 'w');
fwrite($rwis, "Weather Central 001d0300 Surface Data
  18
   6 Station
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
   5 Wind Speed
   5 SubSurface Temp
   5 P1 Temp
   5 P2 Temp
   5 P3 Temp
   5 P4 Temp
   5 Pave Ave Temp
");
 

$now = time();
while ( list($key, $val) = each($mydata) ) {
  $tdiff = $now - $val->db["ts"];

  if ($val->db['tsf0'] == "") $val->db['tsf0'] = -99.99;
  if ($val->db['tsf1'] == "") $val->db['tsf1'] = -99.99;
  if ($val->db['tsf2'] == "") $val->db['tsf2'] = -99.99;
  if ($val->db['tsf3'] == "") $val->db['tsf3'] = -99.99;
  $t = Array($val->db['tsf0'], $val->db['tsf1'],
     $val->db['tsf2'], $val->db['tsf3']);
  arsort($t);
  //print_r($t);
  while (min($t) < -39.99){
    $ba = array_pop($t);
    if (sizeof($t) == 0) break;
  }
  asort($t);
  if (sizeof($t) > 0){
    while ((max($t) - min($t)) > 20){ $ba = array_pop($t); }
    $val->db['pave_avg'] = array_sum($t) / sizeof($t);
  } else {
    $val->db['pave_avg'] = -99.99;
  }
  //echo  $val->db['pave_avg'];



  if ($tdiff < 3600){
  if (round($val->db['rwis_subf'],0) == -100) $val->db['rwis_subf'] = 'M';
  else $val->db['rwis_subf'] = round($val->db['rwis_subf'],0);
  if (round($val->db['tsf0'],0) == -100) $val->db['tsf0'] = 'M';
  else $val->db['tsf0'] = round($val->db['tsf0'],0);
  if (round($val->db['tsf1'],0) == -100) $val->db['tsf1'] = 'M';
  else $val->db['tsf1'] = round($val->db['tsf1'],0);
  if (round($val->db['tsf2'],0) == -100) $val->db['tsf2'] = 'M';
  else $val->db['tsf2'] = round($val->db['tsf2'],0);
  if (round($val->db['tsf3'],0) == -100) $val->db['tsf3'] = '';
  else $val->db['tsf3'] = round($val->db['tsf3'],0);
  if (round($val->db['pave_avg'],0) == -100) $val->db['pave_avg'] = 'M';
  else $val->db['pave_avg'] = round($val->db['pave_avg'],0);

  $s = sprintf("%6s %-52s %2s %7s %8s %2s %4s %5.1f %5.1f %4.0f %4.0f %5.1f %5s %5s %5s %5s %5s %5s\n", $key, 
    $cities[$key]['name'], 'IA', round($cities[$key]['lat'],2), 
     round($cities[$key]['lon'],2),
     date('d', $val->db['ts'] + (6*3600) ), date('H', $val->db['ts'] + (6*3600)),
     $val->db['tmpf'], $val->db['dwpf'],
     $val->db['drct'], drct2txt($val->db['drct']), $val->db['sknt'], 
     fancy($val->db['rwis_subf'],-50,180,5),
     fancy($val->db['tsf0'],-50,180,5), fancy($val->db['tsf1'],-50,180,5),
     fancy($val->db['tsf2'],-50,180,5), fancy($val->db['tsf3'],-50,180,5),
     fancy($val->db['pave_avg'],-50,180,5) ); 
  fwrite($rwis, $s);
  }
} // End of while

fclose($rwis);

`/home/ldm/bin/pqinsert wxc_ildot.txt >& /dev/null`;
`mv wxc_ildot.txt /mesonet/share/pickup/wxc/`;
?>
