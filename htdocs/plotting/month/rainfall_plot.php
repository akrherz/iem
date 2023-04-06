<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";

$station = isset($_GET['station']) ? xssafe($_GET['station']) : "DSM";
$network = isset($_GET['network']) ? xssafe($_GET['network']) : "IA_ASOS";
$month = get_int404('month', date("m"));
$year = get_int404('year', date("Y"));

$uri = sprintf("/plotting/auto/plot/17/month:%s::year:%s::station:%s". 
    "::network:%s::p:precip.png", $month, $year, $station, $network);
header("Location: {$uri}");
