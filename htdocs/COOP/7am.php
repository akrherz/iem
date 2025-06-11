<?php
$OL = "10.4.0";
require_once "../../config/settings.inc.php";
define("IEM_APPID", 86);
require_once "../../include/mlib.php";
force_https();
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Iowa Daily COOP Reports and Comparisons";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" href="7am.css" type="text/css">
EOM;

$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='7am-app.js?v=10'></script>
EOM;

$t->content = <<<EOM
<ol class="breadcrumb">
    <li><a href="/COOP/">NWS COOP</a></li>
    <li class="active">7 AM - 24 Hour Precipitation Analysis</li>
</ol>

<p>The purpose of this application is to provide a visual comparison of
    various datasources for the once daily COOP Reports.</p>
        
<form name="bah">
<div class="row">
<div class="col-md-6">
        <strong>Parameter to Plot:</strong>
    <select id="renderattr">
        <option value='pday'>Precipitation</option>
        <option value='snow'>Snowfall</option>
        <option value='snowd'>Snow Depth [inch]</option>
        <option value='high'>24 Hour High Temperature</option>
        <option value='low'>24 Hour Low Temperature</option>
        <option value='coop_tmpf'>Temperature at Observation Time</option>
    </select>
    <br /><strong>MRMS Legend:</strong> <img src="/images/mrms_q3_p24h.png" />
</div>
<div class="col-md-6">
    <strong>View Date:</strong>
    <button type="button" id="minusday">-1 Day</button>
    <input type="text" id="datepicker" size="30">
    <button type="button" id="plusday">+1 Day</button>
</div>
</div>
</form>

<div id="map" class="map"><div id="popup"></div></div>

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

EOM;
$t->render("full.phtml");
