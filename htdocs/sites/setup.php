<?php
/*
 * I am sourced by all pages on the "sites" website except the 'locate' 
 * frontend.  If station or network are not set, I throw a fit and force the
 * user to the locate page.
 */
 include_once("../../config/settings.inc.php");
 include_once("../../include/database.inc.php");
 include_once("../../include/station.php");
 /* Make sure all is well! */
 $station = isset($_GET["station"]) ? substr($_GET["station"],0,12) : "";
 $network = isset($_GET["network"]) ? $_GET["network"] : "";

$st = new StationData($station, $network);
$cities = $st->table;

 if (strlen($station) == 0)
 {
    header("Location: locate.php");
    die();
 }
 if (! array_key_exists($station, $cities))
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
