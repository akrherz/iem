<?php
/*
 * Dumps IA and IL CoCoRaHS data to a Weather Central formatted file
 */
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";

$rwis = fopen('/tmp/wxc_cocorahs.txt', 'w');
fwrite($rwis, sprintf("Weather Central 001d0300 Surface Data timestamp=%s
  10
  12 Station
  52 CityName
   2 State
   7 Lat
   8 Lon
   2 Day
   4 Hour
   6 Precip Total
   6 Snow Total
   6 Snow Depth
", date("Y.m.d.H.I")) );
 
$states = Array("IA");
$now = time();
foreach($states as $k => $state){
    $arr = Array(
        "network" => "{$state}COCORAHS",
    );
    $jobj = iemws_json("currents.json", $arr);

	foreach($jobj["data"] as $bogus => $val){
  		$tdiff = $now - strtotime($val["local_valid"]);
		if ($tdiff > 86400) continue;
  		
  		if ($val['pday'] < 0) $val["pday"] = " ";
  		if ($val['pday'] == 0.0001) $val["pday"] = "T";
  		if ($val['snowd'] < 0) $val["snowd"] = " ";
  		if ($val['snow'] < 0) $val["snow"] = " ";

  		$s = sprintf("%-12s %-52s %2s %7s %8s %2s %4s %6s %6s %6s\n", $val["station"], 
    $val['name'], $state, round($val['lat'],2), 
     round($val['lon'],2),
  		    date('d', strtotime($val["local_valid"]) + (6*3600) ), date('H', strtotime($val["local_valid"]) + (6*3600)),
     $val['pday'], $val['snow'],
     $val['snowd']);
  		fwrite($rwis, $s);
  		
	} // End of while
}

fclose($rwis);

$pqstr = "data c 000000000000 wxc/wxc_cocorahs.txt bogus txt";
$cmd = sprintf("/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_cocorahs.txt", $pqstr);
system($cmd);
unlink("/tmp/wxc_cocorahs.txt");

?>
