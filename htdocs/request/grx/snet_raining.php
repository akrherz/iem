<?php
header("Content-type: text/plain");

echo 'Title: SchoolNet Where is it raining?
Refresh: 1 
Color: 200 200 255
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("../../../include/database.inc.php");
include("../../../include/mlib.php");
include("../../../include/network.php");
$nt = new NetworkTable(array("KCCI","KIMT","KELO"));
$pgconn = iemdb("iem");

$rs = pg_query($pgconn, "select * from events WHERE 
		valid > now() - '5 minutes'::interval and event = 'P+' ");


for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $lat = $nt->table[$row["station"]]["lat"];
  $lon = $nt->table[$row["station"]]["lon"];

  $hover = sprintf("Name: %s\\n15 minute:%s IN", 
  		$nt->table[$row["station"]]["name"], $row["magnitude"]);

echo "Object: ". $lat .",". $lon ."
  Text:  0, 0, 1, \"".$row["magnitude"]."\", \"$hover\"
 End: 

";
}

?>
