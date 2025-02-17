<?php
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";

$lat = isset($_REQUEST["lat"]) ? xssafe($_REQUEST["lat"]) : die("No lat");
$lon = isset($_REQUEST["lon"]) ? xssafe($_REQUEST["lon"]) : die("No lon");
$day1 = isset($_GET["day1"]) ? xssafe($_GET["day1"]) : die("No day1 specified");
$day2 = isset($_GET["day2"]) ? xssafe($_GET["day2"]) : die("No day2 specified");
$month1 = isset($_GET["month1"]) ? xssafe($_GET["month1"]) : die("No month specified");
$month2 = isset($_GET["month2"]) ? xssafe($_GET["month2"]) : die("No month specified");
$year1 = isset($_GET["year1"]) ? xssafe($_GET["year1"]) : die("No year1 specified");
$year2 = isset($_GET["year2"]) ? xssafe($_GET["year2"]) : die("No year2 specified");

header(
    "Location: /cgi-bin/request/smos.py?lat={$lat}&lon={$lon}".
    "&day1={$day1}&month1={$month1}&year1={$year1}&day2={$day2}&".
    "month2={$month2}&year2={$year2}");
