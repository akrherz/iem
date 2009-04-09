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
IconFile: 1, 32, 32, 16, 16, \"http://mesonet.agron.iastate.edu/request/grx/storm_attribute.png\"
Font: 1, 11, 1, \"Courier New\"
";


for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $d = intval( $row["drct"] ) - 180;
  if ($d < 0){ $d = 360 - $d; }
  $d = 0;
  $ts = strtotime($row["valid"]);
  $q = sprintf("K%s [%s] %s Z\\n", $row["nexrad"], $row["storm_id"], gmdate("H:i", $ts) );
  $q .= sprintf("Drct: %s Speed: %s kts\\n", $row["drct"], $row["sknt"]);
  $icon = 1;
  if ($row["tvs"] != "NONE" || $row["meso"] != "NONE"){
    $q .= sprintf("TVS: %s MESO: %s\\n", $row["tvs"], $row["meso"]);
  }
  if ($row["poh"] != "0" || $row["posh"] != "0"){
    $icon = 2;
    $q .= sprintf("POH: %s POSH: %s MaxSize: %s\\n", $row["poh"], $row["posh"], $row["max_size"]);
  }
  if ($row["meso"] != "NONE"){ $icon = 6; }
  if ($row["tvs"] != "NONE"){ $icon = 5; }
  $q .= sprintf("VIL: %s Max DBZ: %s Hght: %s Top: %s", $row["vil"], $row["max_dbz"], $row["max_dbz_height"] *1000, $row["top"] * 1000);
  echo sprintf("Object: %.4f,%.4f
  Threshold: 999
  Icon: 0,0,%s,1,%s,\"%s\"
END:\n", $row['lat'], $row['lon'], $d, $icon, $q);
}

?>
