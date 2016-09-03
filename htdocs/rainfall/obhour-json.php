<?php
/* Giveme JSON data for zones affected by warning */
include('../../config/settings.inc.php');
include("../../include/database.inc.php");

$connect = iemdb("access");
$mesosite = iemdb("mesosite");

$network = isset($_GET["network"]) ? substr($_GET["network"],0,20) : "IA_ASOS";
$tstr = isset($_GET["ts"]) ? $_GET["ts"]: gmdate("YmdHi");
$ts = mktime( substr($tstr, 8, 2), 0, 0 , 
   substr($tstr, 4, 2), substr($tstr, 6, 2), substr($tstr, 0, 4) );

$networks = "'$network'";
if ($network == "IOWA")
{
  $networks = "'KCCI','IA_ASOS','AWOS','KIMT'";
}

$intervals = Array(1,3,6,12,24,48,72,168,720,"midnight");

$data = Array();
$sql = "SELECT id, name from stations WHERE network IN ($networks)";
$rs = pg_exec($mesosite, $sql);
for($i=0;$z = @pg_fetch_array($rs,$i); $i++)
{
  $data[$z["id"]] = Array(
    "name"=>$z["name"],
    "id"=>$z["id"],
    "pmidnight"=>0,
    "p1"=>0,
    "p3"=>0,
    "p6"=>0,
    "p12"=>0,
    "p24"=>0,
    "p48"=>0,
    "p72"=>0,
    "p96"=>0,
  );
}

while( list($key,$interval) = each($intervals))
{
  if ($interval == "midnight")
  {
    $localts = $ts + date("Z", $ts);
    $ts0 = $ts - (intval(date("H", $localts)) * 3600);
  } else {
    $ts0 = $ts - ($interval * 3600);
  }
  $sql = sprintf("select station, sum(phour) as p1 from hourly_%s
          WHERE valid >= '%s+00' and valid < '%s+00' and network IN (%s) 
          GROUP by station", strftime("%Y", $ts), strftime("%Y-%m-%d %H:%M", $ts0), 
          strftime("%Y-%m-%d %H:%M", $ts), $networks);
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

echo json_encode($ar);

?>
