<?php 
$station = isset($_GET["station"]) ? $_GET["station"] : 'IA2203';
$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");

$url = sprintf("/plotting/auto/?q=99&amp;station=%s&amp;year=%s", $station, $year);
header("Location: $url");
?>