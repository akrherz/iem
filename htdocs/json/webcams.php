<?php
/* Giveme JSON data listing products */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once "$rootpath/include/database.inc.php";

$ts = isset($_REQUEST["ts"]) ? strtotime($_REQUEST["ts"]) : 0;
$network = isset($_REQUEST["network"]) ? substr($_REQUEST["network"],0,4): "KCCI";

$connect = iemdb("mesosite");

if ($ts > 0){
  $result = pg_exec($connect, sprintf("SELECT * from camera_log c, webcams w
    WHERE valid = '%s' and c.cam = w.id and w.network = '%s' ORDER by name ASC", 
    date('Y-m-d H:i', $ts), $network) );
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
     "state" => "",
     "url" => $url);
}
for( $i=0; $row = @pg_fetch_array($result,$i); $i++)
{
  if ($ts > 0){
    $url = sprintf("http://mesonet.agron.iastate.edu/archive/data/%s/camera/%s/%s_%s.jpg", gmdate("Y/m/d", $ts), $row["cam"], $row["cam"], gmdate("YmdHi", $ts) );
  } else {
    $url = "http://mesonet.agron.iastate.edu/data/camera/stills/". $row["cam"] .".jpg"; 
  }
  $z = Array("cid" => $row["id"],
        "name" => $row["name"], 
        "county" => $row["county"], 
        "state" => $row["state"], 
        "url" => $url);
  $ar["images"][] = $z;
}

echo Zend_Json::encode($ar);

?>
