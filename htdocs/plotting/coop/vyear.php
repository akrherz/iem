<?php
$station = isset($_GET["station"]) ? $_GET["station"] : die("No station");
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");

$url = sprintf("/plotting/auto/plot/99/station:%s::network:IACLIMATE::year:%s::dpi:100.png", $station, $year);
header("Location: $url");

?>