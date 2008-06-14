<?php
/* Giveme JSON data for zones affected by warning */
require_once 'Zend/Json.php';
require_once '../../config/settings.inc.php';
require_once 'database.inc.php';

$connect = iemdb("access");
$mesosite = iemdb("mesosite");

$network = isset($_GET["network"]) ? substr($_GET["network"],0,20) : "IA_ASOS";
$ts = mktime(8,0,0,6,13,2008);

$intervals = Array(1,2,3,6,12,24,48,96);

$data = Array();
$sql = "SELECT id, name from stations WHERE network = '$network'";
$rs = pg_exec($mesosite, $sql);
for($i=0;$z = @pg_fetch_array($rs,$i); $i++)
{
  $data[$z["id"]] = Array(
    "name"=>$z["name"],
    "id"=>$z["id"],
    "p1"=>0,
    "p2"=>0,
    "p3"=>0,
    "p6"=>0,
    "p12"=>0,
    "p24"=>0,
    "p48"=>0,
    "p96"=>0,
  );
}

while( list($key,$interval) = each($intervals))
{
  $ts0 = $ts - ($interval * 3600);
  $sql = sprintf("select station, sum(phour) as p1 from hourly_2008 
          WHERE valid >= '%s' and valid < '%s' and network = '%s' 
          GROUP by station", strftime("%Y-%m-%d %H:%M", $ts0), 
          strftime("%Y-%m-%d %H:%M", $ts), $network);
  $rs = pg_exec($connect, $sql);
  for( $i=0; $z = @pg_fetch_array($rs,$i); $i++)
  {
     $data[ $z["station"] ]["p$interval"]  = $z["p1"];
  }
}

$ar = Array("precip" => Array() );
reset($data);
while( list($station,$d) = each($data) )
{
  $ar["precip"][] = $d;
}

echo Zend_Json::encode($ar);

?>
