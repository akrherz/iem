<?php
 /* Make sure all is well! */
 $station = isset($_GET["station"]) ? $_GET["station"] : "";
 if (strlen($station) == 0)
 {
    header("Location: locate.php");
    die();
 }

 $conn = iemdb("mesosite");
 $rs = pg_exec($conn, "SELECT *  from stations WHERE id = '". $station ."'");
 pg_close($conn);

 $row = @pg_fetch_array($rs,0);
 $network = $row["network"];
 $sname = $row["name"];
?>
