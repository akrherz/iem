<?php
$OL = "3.9.0";
include_once "../../config/settings.inc.php";
define("IEM_APPID", 86);
include_once "../../include/myview.php";
$t = new MyView();
$t->title = "7 AM 24 Hour Precipitation Analysis";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol3-layerswitcher.css" rel="stylesheet" />
<style>
.map {
        height: 400px;
        width: 100%;
        background-color: #FFFFFF;
}
.popover {
                width: 300px;
                }
</style>
EOF;

$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol3-layerswitcher.js'></script>
<script src='7am-app.js?v=8'></script>
EOF;

$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/COOP/">NWS COOP</a></li>
	<li class="active">7 AM - 24 Hour Precipitation Analysis</li>
</ol>

<p>The purpose of this application is to provide a visual comparison of
	various datasources for what they show for 24 hour precipitation
	valid at 7 AM local central time.  This application helps in the
	monthly quality control process of Iowa daily climate data.</p>
		
<h4>TODO list</h4>
<ul>
 <li>Add SchoolNet Computed Totals</li>
 <li>Add DCP Computed Totals</li>
 <li>Add CoCoRaHS Totals</li>
 <li>Local Storm Reports</li>
 <li>ISU Soil Moisture Data</li>
 <li>Include nearby state's data</li>
 <li>Add option to plot SWE</li>
 <li>Add Fisher Porter totals</li>
</ul>
		
<form name="bah">
<div class="row">
<div class="col-md-7">
		<strong>Parameter to Plot:</strong>
	<select onChange="javascript: updateMap();" id="renderattr">
		<option value='pday'>Precipitation</option>
		<option value='snow'>Snowfall</option>
		<option value='snowd'>Snow Depth [inch]</option>	
	</select>
	<br /><strong>MRMS Legend:</strong> <img src="/images/mrms_q3_p24h.png" />
</div>
<div class="col-md-5">
		<strong>View Date:</strong>
	<input type="text" id="datepicker" size="30">
</div>
</div>
</form>

<div id="map" class="map"><div id="popup"></div></div>

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>
		

EOF;
$t->render("single.phtml");

?>