<?php
/* Generate GR placefile of Level3 Storm Attributes */
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("postgis");
pg_exec($conn, "SET TIME ZONE 'GMT'");
$nexrad = isset($_GET["nexrad"]) ? substr($_GET["nexrad"],1,3) : False; 
if ($nexrad){
 $rs = pg_prepare($conn, "SELECT", "SELECT *, x(geom) as lon, y(geom) as lat from nexrad_attributes WHERE nexrad = $1");
  $rs = pg_execute($conn, "SELECT", Array($nexrad) );
} else {
 $rs = pg_prepare($conn, "SELECT", "SELECT *, x(geom) as lon, y(geom) as lat from nexrad_attributes");
  $rs = pg_execute($conn, "SELECT", Array());

}

$thres = 999;
$title = "IEM NEXRAD L3 Attributes";
if ($nexrad){ 
  $thres = 45; 
  $title ="IEM $nexrad L3 Attributes";
}
header("Content-type: text/plain");
echo "Refresh: 3
Threshold: $thres
Title: $title
IconFile: 1, 15, 25, 8, 25, \"http://www.spotternetwork.org/icon/arrows.png\"
Font: 1, 11, 1, \"Courier New\"
";


for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $d = intval( $row["drct"] ) - 180;
  if ($d < 0){ $d = 360 - $d; }
  $ts = strtotime($row["valid"]);
  $q = sprintf("ID: %s NEXRAD: K%s Time: %s Z\\n", $row["storm_id"], $row["nexrad"], gmdate("H:i", $ts) );
  echo sprintf("Object: %.4f,%.4f
  Threshold: 999
  Icon: 0,0,%s,1,1,\" %s \"
END:\n", $row['lat'], $row['lon'], $d, $q);
}

?>
