<?php 
/**
 * Produce a map of CLI parsed data for a single day
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 76);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Map of Daily NWS CLImage reports";
$t->thispage = "climate-today";
$OL = '6.3.1';
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<style>
.map {
    height:70vh;
    width: 100%;
}
.popover {
	width: 300px;
}
</style>
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='climap.js?v=10'></script>
EOF;

$t->content = <<<EOF

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<div class="breadcrumb">
		<li><a href="/nws/">NWS Mainpage</a></li>
		<li class="active">Map of NWS Daily CLI Reports</li>
		</div>
		
<div class="row">
<div class="col-md-12">
		
<div class="pull-right">
<i class="fa fa-text-size"></i>
<button id="fminus" class="btn btn-default"><i class="fa fa-minus"></i></button>
<button id="fplus" class="btn btn-default"><i class="fa fa-plus"></i></button>
</div>

		<form name='bah'><p><strong>Select Variable to Plot:</strong> 
<select onChange="javascript: updateMap();" id="renderattr">
	<option value="high">High Temperature</option>
	<option value="high_depart">High Temperature Departure</option>
	<option value="high_record">Record High Temperature</option>
	<option value="high_normal">Normal High Temperature</option>
	<option value="low">Low Temperature</option>
	<option value="low_depart">Low Temperature Departure</option>
	<option value="low_record">Record Low Temperature</option>
	<option value="low_normal">Normal Low Temperature</option>
	<option value="precip">Precipitation</option>
	<option value="precip_month">Precipitation this month</option>
	<option value="precip_jan1">Precipitation since January 1</option>
	<option value="precip_jan1_normal">Precipitation since January 1 Normal</option>
    <option value="precip_jun1">Precipitation since June 1</option>
    <option value="precip_jun1_normal">Precipitation since June 1 Normal</option>
	<option value="precip_dec1">Precipitation since December 1</option>
	<option value="precip_dec1_normal">Precipitation since December 1 Normal</option>
	<option value="precip_record">Precipitation Record</option>
    <option value="precip_month_normal">Precipitation this month normal</option>
	<option value="snow">Snowfall</option>
	<option value="snow_month">Snowfall this month</option>
	<option value="snow_jun1">Snowfall since June 1</option>
	<option value="snow_jul1">Snowfall since July 1</option>
	<option value="snow_jul1_depart">Snowfall since July 1 Departure</option>
	<option value="snow_dec1">Snowfall since December 1</option>
	<option value="snow_record">Snowfall Record</option>
    <option value="resultant_wind_speed">Resultant Wind Speed [mph]</option>
    <option value="resultant_wind_direction">Resultant Wind Direction</option>
    <option value="highest_wind_speed">Highest Wind Speed [mph]</option>
    <option value="highest_wind_direction">Highest Wind Direction</option>
    <option value="highest_gust_speed">Highest Wind Gust [mph]</option>
    <option value="highest_gust_direction">Highest Gust Direction</option>
    <option value="average_wind_speed">Average Wind Speed [mph]</option>
    </select>	
		
<strong>For Date:</strong>
		<input type="text" id="datepicker" size="30">
		
</form>
</div></div><!-- ./row -->

<div class="row">
<div class="col-md-12">

<div id="map" class="map">
<div id="popup"></div>

</div></div><!-- ./row -->

		
<div class="row">
<div class="col-md-12">
    <h4>Click on map to show CLI text below</h4>
	<div id="clireport"></div>
</div>
</div>

EOF;

$t->render('full.phtml');
?>