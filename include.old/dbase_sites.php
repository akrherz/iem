<?php

$connection = pg_connect("10.10.10.40", 5432, "mesosite");
$rs = pg_exec($connection, "SELECT *  from stations WHERE id = '". $station ."' ");
pg_close($connection);

$row = @pg_fetch_array($rs,0);

?>

