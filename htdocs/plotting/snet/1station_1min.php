<?php
$OL = "10.6.1";
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
$network = get_str404("network", "KCCI");

$year = get_int404("year", 2019);
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$station = get_str404('station', "");

$t = new MyView();
$t->iemselect2 = TRUE;
if (!array_key_exists("station", $_GET)) {
    $t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
EOM;
    $t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.js"></script>
EOM;
}
$t->title = "SchoolNet One Minute Time Series";

$nselect = networkSelect($network, $station);
$ys = yearSelect(2002, $year, "year", '', 2019);
$ms = monthSelect($month);
$ds = daySelect($day);

$content = "";
if (strlen($station) > 0) {

    $content .= sprintf("<p><img src=\"1min_T.php?station=%s&amp;year=%s&amp;month=%s&amp;day=%s\" />", $station, $year, $month, $day);
    $content .= sprintf("<p><img src=\"1min_V.php?station=%s&amp;year=%s&amp;month=%s&amp;day=%s\" />", $station, $year, $month, $day);
    $content .= sprintf("<p><img src=\"1min_P.php?station=%s&amp;year=%s&amp;month=%s&amp;day=%s\" />", $station, $year, $month, $day);

    $content .= "<p><b>Note:</b> The wind speeds are indicated every minute by the red line.  The blue dots represent wind direction and are shown every 10 minutes.</p>";
} else {

    $content = <<<EOM

<p>or select from this map...<p>

<div class="row">
<div class="card">
<div class="card-body">
 <div class="col-md-4 col-sm-4">
<a href="?network=KCCI" style="text-decoration: none;">
   <img src="/schoolnet/images/kcci8.jpg" border="0"><br /><b>SchoolNet8</b></a>

 </div>
 <div class="col-md-4 col-sm-4">
<a href="?network=KELO" style="text-decoration: none;">
    <img src="/schoolnet/images/kelo.png" border="0"><br /><b>WeatherNet</b></a>
 </div>
 <div class="col-md-4 col-sm-4">
<a href="?network=KIMT" style="text-decoration: none;">
    <img src="/schoolnet/images/kimt_logo.png" border="0"><br /><b>StormNet</b></a>

    </div></div>

<style type="text/css">
        #map {
            width: 640px;
            height: 400px;
            border: 2px solid black;
        }
</style>
<i>Click black dot to select your site:</i><br />
<div id="map" data-network="{$network}"></div>
EOM;
}

$t->content = <<<EOM
<h3>1 minute data interval time series</h3>

<p>This application generates graphs of 1 minute interval data
for a school based network of your choice. Note that the archive
begins on 12 February 2002, but does not go back that far for
every site.</p>


<form method="GET" action="1station_1min.php" name="olselect">
<input type="hidden" name="network" value="{$network}">
<a href="1station_1min.php?network={$network}">Select Visually</a><br>
Make plot selections: {$nselect}
{$ys} {$ms} {$ds}

<input type="submit" value="Make Plot"></form>

{$content}

</td></tr></table>
</td></tr></table>
EOM;
$t->render('single.phtml');
