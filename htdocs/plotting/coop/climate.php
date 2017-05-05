<?php
$station1 = isset($_GET["station1"]) ? strtoupper($_GET["station1"]) : die("At least 1 station needs to be specified");
$station2 = isset($_GET["station2"]) ? strtoupper($_GET["station2"]) : false;

$url = sprintf("/cgi-bin/climate/daily.py?p=daily&station1=%s", $station1);
if ($station2){
	$url .= sprintf("&station2=%s", $station2);
}
header("Location: $url");
?>