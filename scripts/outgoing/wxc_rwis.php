<?php
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";

function fancy($v, $floor,$ceil, $p){
  if ($v < $floor || $v > $ceil) return "";
  return sprintf("%${p}.1f", $v);
}

include "../../include/database.inc.php";
$pgconn = iemdb('iem');

/* Lets also get the traffic data, please */
$rs = pg_query($pgconn, "select l.nwsli, t.* from rwis_traffic t, 
	rwis_locations l where l.id = t.location_id and lane_id < 4");
$traffic = Array();
for ($i=0;$row=pg_fetch_array($rs);$i++){
	if (! array_key_exists($row["nwsli"], $traffic)){
		$traffic[$row["nwsli"]] = Array("avgspeed0" => "M", 
		"avgspeed1" => "M", "avgspeed2" => "M", "avgspeed3" => "M");
	}
	$traffic[$row["nwsli"]][sprintf("avgspeed%s", $row["lane_id"])] = round($row["avg_speed"],0);
}

$tstamp = gmdate("Y-m-d\TH:i:s");

$jdata = file_get_contents("http://iem.local/api/1/currents.json?network=IA_RWIS");
$jobj = json_decode($jdata, $assoc=TRUE);

$rwis = fopen('/tmp/wxc_iadot.txt', 'w');
fwrite($rwis, "Weather Central 001d0300 Surface Data TimeStamp=$tstamp
  22
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
   3 Sensor 0 Average Speed
   3 Sensor 1 Average Speed
   3 Sensor 2 Average Speed
   3 Sensor 3 Average Speed
");
 


$now = time();
foreach($jobj["data"] as $bogus => $val){
    $key = $val["station"];
	if (! array_key_exists($key,$traffic)){
		$traffic[$key] = Array("avgspeed0" => "M", 
		"avgspeed1" => "M", "avgspeed2" => "M", "avgspeed3" => "M");
	}
  $tdiff = $now - strtotime($val["local_valid"]);

  if ($val['tsf0'] == "") $val['tsf0'] = -99.99;
  if ($val['tsf1'] == "") $val['tsf1'] = -99.99;
  if ($val['tsf2'] == "") $val['tsf2'] = -99.99;
  if ($val['tsf3'] == "") $val['tsf3'] = -99.99;
  $t = Array($val['tsf0'], $val['tsf1'],
     $val['tsf2'], $val['tsf3']);
  arsort($t);
  //print_r($t);
  while (min($t) < -39.99){
    $ba = array_pop($t);
    if (sizeof($t) == 0) break;
  }
  asort($t);
  if (sizeof($t) > 0){
    while ((max($t) - min($t)) > 20){ $ba = array_pop($t); }
    $val['pave_avg'] = array_sum($t) / sizeof($t);
  } else {
    $val['pave_avg'] = -99.99;
  }
  //echo  $val['pave_avg'];



  if ($tdiff < 1800){
  if (round($val['rwis_subf'],0) == -100) $val['rwis_subf'] = 'M';
  else $val['rwis_subf'] = round($val['rwis_subf'],0);
  if (round($val['tsf0'],0) == -100) $val['tsf0'] = 'M';
  else $val['tsf0'] = round($val['tsf0'],0);
  if (round($val['tsf1'],0) == -100) $val['tsf1'] = 'M';
  else $val['tsf1'] = round($val['tsf1'],0);
  if (round($val['tsf2'],0) == -100) $val['tsf2'] = 'M';
  else $val['tsf2'] = round($val['tsf2'],0);
  if (round($val['tsf3'],0) == -100) $val['tsf3'] = 'M';
  else $val['tsf3'] = round($val['tsf3'],0);
  if (round($val['pave_avg'],0) == -100) $val['pave_avg'] = 'M';
  else $val['pave_avg'] = round($val['pave_avg'],0);

  $s = sprintf("%5s %52s %2s %7s %8s %2s %4s %5s %5s %4s %4s %4.1d %4s %4s %4s %4s %4s %4s %3s %3s %3s %3s\n", $key, 
    $val['name'], $val['state'], round($val['lat'],2), 
     round($val['lon'],2),
      date('d', strtotime($val['local_valid']) + (6*3600) ), date('H', strtotime($val['local_valid']) + (6*3600)),
     $val['tmpf'], $val['dwpf'],
     $val['drct'], drct2txt($val['drct']), $val['sknt'], 
     $val['rwis_subf'],
     $val['tsf0'], $val['tsf1'], 
     $val['tsf2'], $val['tsf3'],
     $val['pave_avg'], $traffic[$key]["avgspeed0"],
     $traffic[$key]["avgspeed1"], $traffic[$key]["avgspeed2"],
      $traffic[$key]["avgspeed3"]); 
  fwrite($rwis, $s);
  }
} // End of while

fclose($rwis);

$pqstr = sprintf("data c %s wxc/wxc_iadot.txt bogus txt",
		gmdate("YmdHi"));
$cmd = sprintf("/home/ldm/bin/pqinsert -i -p '%s' /tmp/wxc_iadot.txt",
		$pqstr);
system($cmd);
unlink("/tmp/wxc_iadot.txt");

$jdata = file_get_contents("http://iem.local/api/1/currents.json?network=IL_RWIS");
$jobj = json_decode($jdata, $assoc=TRUE);

$rwis = fopen('/tmp/wxc_ildot.txt', 'w');
fwrite($rwis, "Weather Central 001d0300 Surface Data TimeStamp=$tstamp
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
foreach($jobj["data"] as $bogus => $val){
  $tdiff = $now - strtotime($val["local_valid"]);

  if ($val['tsf0'] == "") $val['tsf0'] = -99.99;
  if ($val['tsf1'] == "") $val['tsf1'] = -99.99;
  if ($val['tsf2'] == "") $val['tsf2'] = -99.99;
  if ($val['tsf3'] == "") $val['tsf3'] = -99.99;
  $t = Array($val['tsf0'], $val['tsf1'],
     $val['tsf2'], $val['tsf3']);
  arsort($t);
  //print_r($t);
  while (min($t) < -39.99){
    $ba = array_pop($t);
    if (sizeof($t) == 0) break;
  }
  asort($t);
  if (sizeof($t) > 0){
    while ((max($t) - min($t)) > 20){ $ba = array_pop($t); }
    $val['pave_avg'] = array_sum($t) / sizeof($t);
  } else {
    $val['pave_avg'] = -99.99;
  }
  //echo  $val['pave_avg'];



  if ($tdiff < 3600){
  if (round($val['rwis_subf'],0) == -100) $val['rwis_subf'] = 'M';
  else $val['rwis_subf'] = round($val['rwis_subf'],0);
  if (round($val['tsf0'],0) == -100) $val['tsf0'] = 'M';
  else $val['tsf0'] = round($val['tsf0'],0);
  if (round($val['tsf1'],0) == -100) $val['tsf1'] = 'M';
  else $val['tsf1'] = round($val['tsf1'],0);
  if (round($val['tsf2'],0) == -100) $val['tsf2'] = 'M';
  else $val['tsf2'] = round($val['tsf2'],0);
  if (round($val['tsf3'],0) == -100) $val['tsf3'] = '';
  else $val['tsf3'] = round($val['tsf3'],0);
  if (round($val['pave_avg'],0) == -100) $val['pave_avg'] = 'M';
  else $val['pave_avg'] = round($val['pave_avg'],0);

  $s = sprintf("%6s %-52s %2s %7s %8s %2s %4s %5.1f %5.1f %4.0f %4.0f %5.1f %5s %5s %5s %5s %5s %5s\n",
      $val["station"], $val['name'], $val['state'], round($val['lat'],2), 
     round($val['lon'],2),
     date('d', strtotime($val['local_valid']) + (6*3600) ), date('H', strtotime($val['local_valid']) + (6*3600)),
     $val['tmpf'], $val['dwpf'],
     $val['drct'], drct2txt($val['drct']), $val['sknt'], 
     fancy($val['rwis_subf'],-50,180,5),
     fancy($val['tsf0'],-50,180,5), fancy($val['tsf1'],-50,180,5),
     fancy($val['tsf2'],-50,180,5), fancy($val['tsf3'],-50,180,5),
     fancy($val['pave_avg'],-50,180,5) ); 
  fwrite($rwis, $s);
  }
} // End of while

fclose($rwis);

$pqstr = sprintf("data c %s wxc/wxc_ildot.txt bogus txt",
		gmdate("YmdHi"));
$cmd = sprintf("/home/ldm/bin/pqinsert -i -p '%s' /tmp/wxc_ildot.txt",
		$pqstr);
system($cmd);
unlink("/tmp/wxc_ildot.txt");

?>