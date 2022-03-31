<?php
require_once '../../config/settings.inc.php';
require_once "../../include/database.inc.php";

$connect = iemdb("iem");
$mesosite = iemdb("mesosite");

$network = isset($_GET["network"]) ? substr($_GET["network"],0,20) : "IA_ASOS";
$tstr = isset($_GET["ts"]) ? $_GET["ts"]: gmdate("YmdHi");
$ts = mktime( substr($tstr, 8, 2), 0, 0 , 
   substr($tstr, 4, 2), substr($tstr, 6, 2), substr($tstr, 0, 4) );

$networks = "'$network'";
if ($network == "IOWA")
{
  $networks = "'KCCI','IA_ASOS','KIMT'";
}

$intervals = Array(1,3,6,12,24,48,72,168,720,"midnight");

$data = Array();
$sql = "SELECT id, name from stations WHERE network IN ($networks)";
$rs = pg_exec($mesosite, $sql);
for($i=0;$z = pg_fetch_array($rs); $i++)
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

foreach($intervals as $key => $interval)
{
  if ($interval == "midnight")
  {
    $localts = $ts + date("Z", $ts);
    $ts0 = $ts - (intval(date("H", $localts)) * 3600);
  } else {
    $ts0 = $ts - ($interval * 3600);
  }
  $sql = sprintf("select id as station, sum(phour) as p1 from hourly_%s h ".
      "JOIN stations t on (h.iemid = t.iemid) WHERE valid >= '%s+00' and ".
      "valid < '%s+00' and t.network IN (%s) ".
      "GROUP by t.id",
      strftime("%Y", $ts), strftime("%Y-%m-%d %H:%M", $ts0), 
          strftime("%Y-%m-%d %H:%M", $ts), $networks);
  $rs = pg_exec($connect, $sql);
  for( $i=0; $z = pg_fetch_array($rs); $i++)
  {
      // hackery to account for trace values
      $val = floatval($z["p1"]);
      if ($val > 0.005){
          $retval = sprintf("%.2f", $val);
      } else if ($val > 0){
          $retval = "T";
      } else{
          $retval = "0";
      }
     $data[ $z["station"] ]["p$interval"]  = $retval;
  }
}

$ar = Array("precip" => Array() );
foreach($data as $station => $d)
{
  $ar["precip"][] = $d;
}

echo json_encode($ar);

?>
