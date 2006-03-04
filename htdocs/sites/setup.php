<?php
 include_once("../../config/settings.inc.php");
 include_once("$rootpath/include/database.inc.php");
 include_once("$rootpath/include/all_locs.php");
 /* Make sure all is well! */
 $station = isset($_GET["station"]) ? $_GET["station"] : "";
 $network = isset($_GET["network"]) ? $_GET["network"] : "";
 if (strlen($station) == 0)
 {
    header("Location: locate.php");
    die();
 }
 if (! isset($_GET["network"]) )
 {
    $network = $cities[$station]["network"];
 }
 $metadata = $cities[$station];
?>
