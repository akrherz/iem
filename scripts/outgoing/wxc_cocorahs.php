<?php
/*
 * Dumps IA and IL CoCoRaHS data to a Weather Central formatted file
 */
include("../../config/settings.inc.php");
include("../../include/mlib.php");

include("../../include/network.php");
$nt = new NetworkTable("IACOCORAHS");
include("../../include/iemaccess.php");
include("../../include/iemaccessob.php");
$iem = new IEMAccess();


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
reset($states);
$now = time();
while(list($k,$state) = each($states)){

	$mydata = $iem->getNetwork("${state}COCORAHS");

	while ( list($key, $val) = each($mydata) ) {
  		$tdiff = $now - $val->db["ts"];
		if ($tdiff > 86400) continue;
  		
  		if ($val->db['pday'] < 0) $val->db["pday"] = " ";
  		if ($val->db['pday'] == 0.0001) $val->db["pday"] = "T";
  		if ($val->db['snowd'] < 0) $val->db["snowd"] = " ";
  		if ($val->db['snow'] < 0) $val->db["snow"] = " ";

  		$s = sprintf("%-12s %-52s %2s %7s %8s %2s %4s %6s %6s %6s\n", $key, 
    $nt->table[$key]['name'], $state, round($nt->table[$key]['lat'],2), 
     round($nt->table[$key]['lon'],2),
     date('d', $val->db['ts'] + (6*3600) ), date('H', $val->db['ts'] + (6*3600)),
     $val->db['pday'], $val->db['snow'],
     $val->db['snowd']);
  		fwrite($rwis, $s);
  		
	} // End of while
}

fclose($rwis);

$pqstr = "data c 000000000000 wxc/wxc_cocorahs.txt bogus txt";
$cmd = sprintf("/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_cocorahs.txt", $pqstr);
system($cmd);
unlink("/tmp/wxc_cocorahs.txt");

?>
