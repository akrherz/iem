<?php
/* Need something to fetch IEM Properties */
include_once("$rootpath/include/database.inc.php");

function get_iemprop($propname){
  $dbconn = iemdb("mesosite");
  $rs = pg_prepare($dbconn, "SELECT321", "SELECT * from properties where
        propname = $1");
  $rs = pg_execute($dbconn, "SELECT321", Array($propname));
  if (pg_num_rows($rs) < 1){ return null; }
  $row = pg_fetch_array($rs,0);
  return $row["propvalue"];
}
?>
