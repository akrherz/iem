<?php
header("Content-type: text/plain");

echo 'Title: SchoolNet Where is it raining?
Refresh: 1 
Color: 200 200 255
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/snet_locs.php");
$pgconn = iemdb("access");

$rs = pg_query($pgconn, "select * from events WHERE valid > now() - '5 minutes'::interval and event = 'P+' ");


for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $lat = $cities[$row["network"]][$row["station"]]["lat"];
  $lon = $cities[$row["network"]][$row["station"]]["lon"];

  $hover = sprintf("Name: %s\\n15 minute:%s IN", $cities[$row["network"]][$row["station"]]["city"], $row["magnitude"]);

echo "Object: ". $lat .",". $lon ."
  Text:  0, 0, 1, \"".$row["magnitude"]."\", \"$hover\"
 End: 

";
}

?>
