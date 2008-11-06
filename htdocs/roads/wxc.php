<?php
/* Generate WXC stationfile with the road conditons */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb("postgis");


header("Content-type: text/plain");

$sql = "SELECT x(transform(centroid(b.geom),4326)) as lon, 
               y(transform(centroid(b.geom),4326)) as lat,
      * from roads_current r, roads_base b, roads_conditions c WHERE
  r.segid = b.segid and r.cond_code = c.code";

$rs = pg_query($conn, $sql);



echo "Weather Central 001d0300 Surface Data\r\n 12\r\n   5 Station\r\n   8 Timestamp\r\n   3 Road Condition Code\r\n   1 Towing Ban\r\n   1 Limited Visibility\r\n   9 Latitude\r\n   9 Longitude\r\n   1 Road Type\r\n  10 Road Major\r\n  64 Road Minor\r\n 64 Simple Condition Text\r\n 128 Full Condition Text\r\n";


for ($i=0; $row = @pg_fetch_array($rs, $i); $i++)
{
  $seg = intval($row["segid"]);
  $minor = $row["minor"];
  $major = $row["major"];
  if ($row["type"] == 1){ $number = intval($row["int1"]); }
  if ($row["type"] == 2){ $number = intval($row["us1"]); }
  if ($row["type"] == 3){ $number = intval($row["st1"]); }
  $lbl = $row["label"];
  $raw = $row["raw"];
  $ccode = $row["code"];
  $lon = $row["lon"];
  $lat = $row["lat"];
  $ts = date("h:i A", strtotime($row["valid"]));

  echo sprintf("%-5s %8s %-3s %1s %1s %9.4f %9.4f %1s %-10s %-64s %-64s %-128s\r\n", $seg, $ts, $ccode, strtoupper($row["towing_prohibited"]), strtoupper($row["limited_vis"]), $lat, $lon, $row["type"],$major, $minor, $lbl, $raw);
}


?>
