<?php
/* Generate GR placefile of webcam stuff */
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/cameras.inc.php");
$network = isset($_GET["network"]) ? $_GET["network"] : "KCCI"; 
$overview = isset($_GET["overview"]);

$thres = 999;
if (!$overview) $thres = 15;
header("Content-type: text/plain");
echo "Refresh: 1
Threshold: $thres
Title: $network webcams via IEM
IconFile: 1, 15, 25, 8, 25, \"http://www.spotternetwork.org/icon/arrows.png\"
";

$conn = iemdb("mesosite");

$sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval)"; 
$s2 = "";
$s3 = "";
$q = 2;
$rs = pg_exec($conn, $sql);
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $key = $row["cam"];
  if ($cameras[$key]["network"] != $network){ continue; }
  if (!$overview)
  echo sprintf("IconFile: %s, 320, 240, 160, 240,\"http://mesonet.agron.iastate.edu/data/camera/stills/%s.jpg\"\n", $q, $key);
  $s2 .= sprintf("Icon: %.4f,%.4f,%s,1,5,\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $row["drct"]);
  $s3 .= sprintf("Icon: %.4f,%.4f,000,%s,1,\"[%s] %s\"\n", $cameras[$key]['lat'], $cameras[$key]['lon'], $q, $cameras[$key]["network"], $cameras[$key]["name"]);
  $q += 1;
}
echo $s2;
  if (!$overview)
echo $s3;

?>
