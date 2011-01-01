<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$access = iemdb('access');
$conn = iemdb('afos');

$pil = strtoupper($_REQUEST["pil"]);
$cnt = $_REQUEST["cnt"];

/*
 * We need to optimize some things here, first search the current table
 * and see if we can come up with enough entries.
 * TODO
 */
$table = sprintf("products_%s_", date("Y"));
if (intval(date("m")) > 6){
	$table .= "0712";
} else {
	$table .= "0106";
}
/* Okay, lets try the local table first */
$rs = pg_prepare($conn, "LSELECT", "SELECT * from $table WHERE pil = $1
                         ORDER by entered DESC LIMIT $2");
$rs = pg_execute($conn, "LSELECT", Array($pil, $cnt));
if (pg_num_rows($rs) != $cnt){
	/* Our optimization failed, shucks */
	$rs = pg_prepare($conn, "SELECT", "SELECT * from products WHERE pil = $1
                         ORDER by entered DESC LIMIT $2");

	$rs = pg_execute($conn, "SELECT", Array($pil, $cnt));
}


if (pg_numrows($rs) == 0){
 if (substr($pil,0,3) == "MTR"){
   $rs = pg_prepare($access, "SELECT2", "SELECT raw from current_log WHERE
         raw != '' and station = $1 ORDER by valid DESC LIMIT $2");
   $rs = pg_execute($access, "SELECT2", Array(substr($pil,3,3), $cnt));
   for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
   {
      echo "<pre>". $row["raw"] ."</pre><hr />";
   }
   if (pg_numrows($rs) > 0){ die(); }

 }
}
if (pg_numrows($rs) == 0){
   echo "<h3>No entries found for ${pil}</h3>";
   die();
}

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{ 
  echo "<pre>". $row["data"] ."</pre><hr />";
}

?>
