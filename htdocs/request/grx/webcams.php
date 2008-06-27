<?php
/* Generate GR placefile of webcam stuff */
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/cameras.inc.php");
$network = isset($_GET["network"]) ? $_GET["network"] : "KCCI"; 

header("Content-type: text/plain");
echo " Refresh: 1
  Threshold: 999
  Title: IEM Delivered Webcams
  IconFile: 1, 15, 25, 8, 25, \"http://www.spotternetwork.org/icon/arrows.png\"
";
$q = 2;
while (list($key,$val) = each($cameras)){
  if ($cameras[$key]["network"]) != $network){ continue; }
  $cameras[$key]["q"] = $q;
  echo sprintf("IconFile: %s, 320, 240, 160, 240,\"http://mesonet.agron.iastate.edu/data/camera/stills/%s.jpg\"\n", $q, $key);
  $q += 1;
}

$conn = iemdb("mesosite");

$sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval)"; 
$rs = pg_exec($conn, $sql);
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $key = $row["cam"];
  if ($cameras[$key]["network"]) != $network){ continue; }
  echo sprintf("Icon: %.4f,%.4f,%s,1,5,\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $row["drct"]);
  echo sprintf("Icon: %.4f,%.4f,000,%s,1,\"[%s] %s\"\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $cameras[$key]["q"], $cameras[$key]["network"], $cameras[$key]["name"]);
}

?>
