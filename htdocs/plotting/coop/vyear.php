<?php
$station = isset($_GET["station"]) ? $_GET["station"] : die("No station");
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");

$url = sprintf("/cgi-bin/climate/daily.py?p=compare&station1=%s", $station1);
header("Location: $url");

?>

