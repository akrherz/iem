<?php 
 include("../../../config/settings.inc.php");
 include_once "../../../include/myview.php";
 $t = new MyView();
 
 include("../../../include/forms.php");
 include("../../../include/imagemaps.php"); 
 $network = isset($_REQUEST["network"]) ? $_REQUEST["network"]: "KCCI";
 
$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$station = isset($_GET['station'] ) ? $_GET['station'] : "";
 
if (! isset($_GET["station"])){
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/3.5.0/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/3.5.0/ol3-layerswitcher.css" rel="stylesheet" />
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/3.5.0/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/3.5.0/ol3-layerswitcher.js'></script>
<script src="/js/olselect.php?network=${network}"></script>
EOF;
}
$t->title = "SchoolNet One Minute Time Series";
$t->thispage = "networks-schoolnet"; 

$nselect = networkSelect($network, $station); 
$ys = yearSelect2(2002, $year, "year");
$ms = monthSelect($month);
$ds = daySelect($day);

$content = "";
if (strlen($station) > 0 ) {

	$content .= sprintf("<p><img src=\"1min_T.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day);
	$content .= sprintf("<p><img src=\"1min_V.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day);
	$content .= sprintf("<p><img src=\"1min_P.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day);

	$content .= "<p><b>Note:</b> The wind speeds are indicated every minute by the red line.  The blue dots represent wind direction and are shown every 10 minutes.</p>";

} else {
	
	$content = <<<EOF

<p>or select from this map...<p>

<div class="row well">
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
<div id="map"></div>
EOF;
 }


$t->content = <<<EOF
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
EOF;
$t->render('single.phtml');
?>
