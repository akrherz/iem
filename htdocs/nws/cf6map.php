<?php

/**
 * Produce a map of CF6 parsed data for a single day
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 131);
require_once "../../include/myview.php";
require_once "../../include/mlib.php";
force_https();
$t = new MyView();
$t->title = "Map of Daily NWS CF6 reports";
$OL = '7.2.2';
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.12.1/jquery-ui.min.css" />
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
<script src="/vendor/jquery-ui/1.12.1/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='cf6map.js'></script>
EOF;

$t->content = <<<EOF

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<div class="breadcrumb">
        <li><a href="/nws/">NWS Mainpage</a></li>
        <li class="active">Map of NWS Daily CF6 Reports</li>
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
    <option value="low">Low Temperature</option>
    <option value="avg_temp">Average Temperature</option>
    <option value="dep_temp">Average Temperature Depature</option>
    <option value="hdd">Heating Degree Days</option>
    <option value="cdd">Cooling Degree Days</option>
    <option value="precip">Precipitation</option>
    <option value="snow">Snowfall</option>
    <option value="snowd_12z">Snow Depth at 12z</option>
    <option value="avg_smph">Average Wind Speed</option>
    <option value="max_smph">Max Wind Speed</option>
    <option value="avg_drct">Average Wind Direction</option>
    <option value="minutes_sunshine">Minutes Sunshine</option>
    <option value="possible_sunshine">Possible Sunshine</option>
    <option value="cloud_ss">Cloud SS</option>
    <option value="wxcodes">wxcodes</option>
    <option value="gust_smph">Wind Gust</option>
    <option value="gust_drct">Wind Gust Direction</option>
    </select>	
        
<strong>For Date:</strong><input type="text" id="datepicker" size="30">
        
</form>
</div></div><!-- ./row -->

<div class="row">
<div class="col-md-12">

<div id="map" class="map">
<div id="popup"></div>

</div></div><!-- ./row -->

        
<div class="row">
<div class="col-md-12">
    <h4>Click on map to show CF6 text below</h4>
    <div id="cf6report"></div>
</div>
</div>

EOF;

$t->render('full.phtml');
