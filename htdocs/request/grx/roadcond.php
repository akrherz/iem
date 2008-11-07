<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$conn = iemdb('postgis');

header("Content-type: text/plain");

$colors = Array(
   0 => "255 255 255",
    1 => "0 204 0",
    3 => "152 152 152",
    7 => "152 152 152",
    11 => "152 152 152",
    15 => "255 197 197",
    19 => "254 51 153",
    23 => "181 0 181",
    27 => "255 197 197",
    31 => "254 51 153",
    35 => "181 0 181",
    39 => "153 255 255",
    43 => "0 153 254",
    47 => "0 0 158",
    51 => "232 95 1",
    56 => "255 197 197",
    60 => "254 51 153",
    86 => "255 0 0");



echo "Threshold: 999
Title: IEM Delivered Iowa Road Conditions
";

$rs = pg_query($conn, "SELECT astext(transform(simple_geom,4326)) as t, * from roads_current_test r, roads_base b, roads_conditions c WHERE r.segid = b.segid and r.cond_code = c.code");

for ($i=0;$row= @pg_fetch_array($rs,$i);$i++)
{
  echo "Color: ". $colors[$row["cond_code"]] ."\n";
  echo "Line: 4, 0, ". $row["major"] ."\n";
  $meat = str_replace("MULTILINESTRING((", "", $row["t"]);
  $meat = str_replace("))", "", $meat);
  $tokens = explode(",", $meat);
  while (list($q,$s) = each($tokens)){
    $t = explode(" ", $s);
    echo sprintf("%.3f, %.3f", $t[1], $t[0]) ."\n";
  }
  echo "End:\n";
}

?>
