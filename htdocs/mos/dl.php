<?php
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";

$year1 = get_int404("year1", date("Y", time() + 86400));
$year2 = get_int404("year2", date("Y", time() + 86400));
$month1 = get_int404("month1", date("m", time() + 86400));
$month2 = get_int404("month2", date("m", time() + 86400));
$day1 = get_int404("day1", date("d", time() + 86400));
$day2 = get_int404("day2", date("d", time() + 86400));
$hour1 = get_int404("hour1", 0);
$hour2 = get_int404("hour2", 12);
$model = isset($_GET["model"]) ? xssafe($_GET["model"]) : "GFS";
$station = isset($_GET["station"]) ? strtoupper(xssafe($_GET["station"])) : "KAMW";

$url = sprintf(
    "/cgi-bin/request/mos.py?year1=%s&year2=%s&month1=%s&month2=%s&" .
    "day1=%s&day2=%s&hour1=%s&hour2=%s&model=%s&station=%s",
    $year1, $year2, $month1, $month2, $day1, $day2, $hour1, $hour2,
    $model, $station,
);
header("Location: $url");
