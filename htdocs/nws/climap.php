<?php 
/**
 * Produce a map of CLI parsed data for a single day
 */
include("../../config/settings.inc.php");
define("IEM_APPID", -99);
include "../../include/myview.php";
$t = new MyView();
$t->title = "Map of Daily NWS CLImage reports";
$t->thispage = "climate-today";

$t->headextra = <<<EOF
<link rel="stylesheet" href="http://openlayers.org/en/v3.0.0/css/ol.css" type="text/css">
<link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
<link rel="stylesheet" type="text/css" href="/css/jquery.datetimepicker.css"/ >
<style>
.map {
	height: 400px;
	width: 100%;
}
.popover {
		width: 300px;
		}
</style>
EOF;
$t->jsextra = <<<EOF
<script src="http://openlayers.org/en/v3.0.0/build/ol-debug.js" type="text/javascript"></script>
<script src="http://code.jquery.com/ui/1.10.4/jquery-ui.js"></script>
<script src='climap.js?v=3'></script>
EOF;
$t->bodyextra = "onload=\"init()\"";

$t->content = <<<EOF

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<div class="row">
<div class="col-md-12">
		
<form name='bah'><p><strong>Select Variable to Plot:</strong> 
<select onChange="javascript: updateMap();" id="renderattr">
	<option value="high">High Temperature</option>
	<option value="high_record">Record High Temperature</option>
	<option value="high_normal">Normal High Temperature</option>
	<option value="low">Low Temperature</option>
	<option value="low_record">Record Low Temperature</option>
	<option value="low_normal">Normal Low Temperature</option>
</select>	
		
<strong>For Date:</strong>
		<input type="text" id="datepicker">
		
</form>
		
<div id="map" class="map">
		<div id="popup"></div>
		</div>

</div></div>
		
<h4>Click on map to show CLI text below</h4>
<div class="row">
<div class="col-md-12">
	<div id="clireport"></div>
</div></div>

EOF;

$t->render('single.phtml');
?>