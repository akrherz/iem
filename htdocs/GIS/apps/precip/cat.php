<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
if (strlen($verbose) > 0){
header("Content-type: text/plain");
} else {
header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=iemprecip.txt");
}
/**
 * cat.php
 *   Send out downloadable data from current table
 */

 $vardict = Array("p01i" => "Last Hour Accumulation",
    "p24i" => "Last 24 Hour Accumulation",
    "p12z" => "24 Hour Accumulation ending 12Z",
    "pday" => "Today's Accumulation");

 $connection = iemdb("access");
 $var = substr($param, 0, 4);

 $query = "SELECT ".$var." as data, station, X(geom) as x, Y(geom) as y 
   from current WHERE ".$var." >= 0 and valid > 'TODAY'";
 $rs = pg_exec($connection, $query);

 $query = "SELECT ".$var." as ts from current_meta";
 $meta = pg_exec($connection, $query);

 pg_close($connection);

 if (strlen($verbose) > 0){
   echo "# IEM | RAW Precipitation Report\n";
   echo "# Numbers are unofficial and subject to revision.\n";

   $row = @pg_fetch_array($meta, 0);
   echo "# Last Data Update: ". $row["ts"] ."\n";
   echo "# Variable: ".$var." -> ". $vardict[$var] ."\n";
 }

 echo "station,long,lat,".$var."\n";

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  $val = $row["data"];
  $station = $row["station"];
  $x = $row["x"];
  $y = $row["y"];

  echo $station.",".$x.",".$y.",".$val."\n";

 } // End of for
?>

