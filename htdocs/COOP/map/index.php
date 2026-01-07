<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 168);
require_once "../../../include/myview.php";
require_once "../../../include/mlib.php";
require_once "../../../include/forms.php";
force_https();

// Handle URL parameters for date and variable selection
$date_param = get_str404("date", date("Y-m-d"));
$var_param = get_str404("var", "high");

// Validate date parameter
$valid_date = $date_param;
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date_param) || !strtotime($date_param)) {
    $valid_date = date("Y-m-d");
}

// Define available render variables with their display names
$render_vars = [
    "high" => "High Temperature (°F)",
    "low" => "Low Temperature (°F)",
    "coop_tmpf" => "Observation Temperature (°F)",
    "precip" => "Precipitation (inch)",
    "snow" => "Snowfall (inch)",
    "snowd" => "Snow Depth (inch)",
];

// Validate variable parameter
$valid_var = array_key_exists($var_param, $render_vars) ? $var_param : "high";

// Generate select element using helper function
$render_select = make_select("renderattr", $valid_var, $render_vars, "", "form-select", FALSE, FALSE, TRUE, ["id" => "renderattr"]);

$t = new MyView();
$t->title = "Map of Daily NWS COOP Reports";
$OL = '10.7.0';
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="index.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='index.js?v=9'></script>
EOM;

$t->content = <<<EOM

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<nav aria-label="breadcrumb">
<ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
        <li class="breadcrumb-item active" aria-current="page">Map of NWS Daily COOP Reports</li>
</ol>
</nav>

<div class="row">
<div class="col-12">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="mb-0">Map of NWS Daily COOP Reports</h4>
        <div class="btn-group" role="group" aria-label="Font size controls">
            <button id="fminus" class="btn btn-outline-secondary btn-sm" type="button"
                title="Decrease font size">
                <i class="bi bi-dash" aria-hidden="true"></i>
            </button>
            <span class="btn btn-outline-secondary btn-sm disabled">
                <i class="bi bi-text-paragraph" aria-hidden="true"></i>
            </span>
            <button id="fplus" class="btn btn-outline-secondary btn-sm" type="button"
                title="Increase font size">
                <i class="bi bi-plus" aria-hidden="true"></i>
            </button>
        </div>
    </div>

    <form name='climapform' class="mb-4">
        <div class="row g-3 align-items-end">
            <div class="col-md-6">
                <label for="renderattr" class="form-label">Select Variable to Plot:</label>
                {$render_select}
            </div>
            <div class="col-md-4">
                <label for="datepicker" class="form-label">Select Date:</label>
                <input type="date" id="datepicker" class="form-control" value="{$valid_date}">
            </div>
        </div>
    </form>
</div></div><!-- ./row -->

<div class="row">
<div class="col-12">
    <div id="map" class="map">
        <div id="popup"></div>
    </div>
</div>
</div>

EOM;

$t->render('full.phtml');
