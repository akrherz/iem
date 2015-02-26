<?php 
include_once "../../config/settings.inc.php";
define("IEM_APPID", 86);
include_once "../../include/myview.php";
$t = new MyView();
$t->title = "12 UTC 24 Hour Precipitation Analysis";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/assets/openlayers/3.2.1/css/ol.css" type="text/css">
<link rel="stylesheet" href="/assets/jquery-ui/1.11.2/jquery-ui.min.css" />
<link type="text/css" href="/assets/openlayers/3.2.1/css/ol3-layerswitcher.css" rel="stylesheet" />
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
<script src="/assets/openlayers/3.2.1/build/ol.js" type="text/javascript"></script>
<script src="/assets/jquery-ui/1.11.2/jquery-ui.js"></script>
<script src='/assets/openlayers/3.2.1/build/ol3-layerswitcher.js'></script>
<script src='12z-app.js?v=6'></script>
EOF;

$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/COOP/">NWS COOP</a></li>
	<li class="active">12 UTC - 24 Hour Precipitation Analysis</li>
</ol>
<form name="bah">
<div class="row">
<div class="col-md-7">
		<strong>Parameter to Plot:</strong>
	<select onChange="javascript: updateMap();" id="renderattr">
		<option value='pday'>Precipitation</option>
		<option value='snow'>Snowfall</option>
		<option value='snowd'>Snow Depth [inch]</option>	
	</select>
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