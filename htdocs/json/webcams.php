<?php header('content-type: application/json; charset=utf-8');
/*
 *  Giveme JSON data listing of webcams 
 */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

// This should be a UTC timestamp, gasp!
$ts = isset($_REQUEST["ts"]) ? strtotime($_REQUEST["ts"]) : 0;
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,4): "KCCI";

$connect = iemdb("mesosite");
pg_exec($connect, "SET TIME ZONE 'GMT'");

if ($ts > 0){
	if ($network != "IDOT"){
  		$result = pg_exec($connect, sprintf("SELECT * from camera_log c, webcams w
    		WHERE valid = '%s' and c.cam = w.id and w.network = '%s' ORDER by name ASC", 
    		date('Y-m-d H:i', $ts), $network) );
	} else {
		$result = pg_exec($connect, sprintf("SELECT * from camera_log c, webcams w
    		WHERE valid BETWEEN '%s'::timestamp - '10 minutes'::interval
			and '%s'::timestamp + '10 minutes'::interval and c.cam = w.id 
			and w.network = '%s' ORDER by name ASC, valid ASC",
			date('Y-m-d H:i', $ts), date('Y-m-d H:i', $ts), $network) );
	}
} else {
  $result = pg_exec($connect, "SELECT * from camera_current c, webcams w 
  WHERE valid > (now() - '15 minutes'::interval) 
  and c.cam = w.id and w.network = '$network'
  ORDER by name ASC");
}



$ar = Array("images" => Array() );
if ($ts > 0){
  $url = "http://mesonet.agron.iastate.edu/current/camrad.php?network=${network}&ts=". $_REQUEST["ts"];
} else {
  $url = "http://mesonet.agron.iastate.edu/current/camrad.php?network=${network}";
}
if (pg_num_rows($result) > 0){
  $ar["images"][] = Array("cid" => "${network}-000",
     "name" => " NEXRAD Overview",
     "county" => "",
     "network" => "",
     "state" => "",
     "url" => $url);
}
$used = Array();
for( $i=0; $row = @pg_fetch_assoc($result,$i); $i++)
{
	if (array_key_exists($row["cam"], $used)){
		continue;
	}
	$used[$row["cam"]] = True;
	$gts = strtotime($row["valid"]);
    $url = sprintf("http://mesonet.agron.iastate.edu/archive/data/%s/camera/%s/%s_%s.jpg", 
    		gmdate("Y/m/d", $gts), $row["cam"], $row["cam"], gmdate("YmdHi", $gts) );
  	$z = Array("cid" => $row["id"],
        "name" => $row["name"], 
        "county" => $row["county"], 
        "state" => $row["state"], 
  		"network" => $row["network"],
        "url" => $url);
  	$ar["images"][] = $z;
}

$json = Zend_Json::encode($ar);

# JSON if no callback
if( ! isset($_GET['callback']))
	exit( $json );

exit( "{$_GET['callback']}($json)" );
?>
