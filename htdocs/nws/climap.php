<?php
// Produce a map of CLI parsed data for a single day
require_once "../../config/settings.inc.php";
define("IEM_APPID", 76);
require_once "../../include/myview.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";
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
    "high" => "High Temperature",
    "high_depart" => "High Temperature Departure",
    "high_record" => "Record High Temperature",
    "high_normal" => "Normal High Temperature",
    "low" => "Low Temperature",
    "low_depart" => "Low Temperature Departure",
    "low_record" => "Record Low Temperature",
    "low_normal" => "Normal Low Temperature",
    "precip" => "Precipitation",
    "precip_month" => "Precipitation this month",
    "precip_jan1" => "Precipitation since January 1",
    "precip_jan1_normal" => "Precipitation since January 1 Normal",
    "precip_jan1_depart" => "Precipitation since January 1 Departure",
    "precip_jun1" => "Precipitation since June 1",
    "precip_jun1_normal" => "Precipitation since June 1 Normal",
    "precip_dec1" => "Precipitation since December 1",
    "precip_dec1_normal" => "Precipitation since December 1 Normal",
    "precip_record" => "Precipitation Record",
    "precip_month_normal" => "Precipitation this month normal",
    "snow" => "Snowfall",
    "snowdepth" => "Snow Depth [inch]",
    "snow_month" => "Snowfall this month",
    "snow_jun1" => "Snowfall since June 1",
    "snow_jul1" => "Snowfall since July 1",
    "snow_jul1_depart" => "Snowfall since July 1 Departure",
    "snow_dec1" => "Snowfall since December 1",
    "snow_record" => "Snowfall Record",
    "resultant_wind_speed" => "Resultant Wind Speed [mph]",
    "resultant_wind_direction" => "Resultant Wind Direction",
    "highest_wind_speed" => "Highest Wind Speed [mph]",
    "highest_wind_direction" => "Highest Wind Direction",
    "highest_gust_speed" => "Highest Wind Gust [mph]",
    "highest_gust_direction" => "Highest Gust Direction",
    "average_wind_speed" => "Average Wind Speed [mph]"
];

// Validate variable parameter
$valid_var = array_key_exists($var_param, $render_vars) ? $var_param : "high";

// Generate select element using helper function
$render_select = make_select("renderattr", $valid_var, $render_vars, "", "form-select", FALSE, FALSE, TRUE, ["id" => "renderattr"]);

$t = new MyView();
$t->title = "Map of Daily NWS CLImage reports";
$OL = '10.5.0';
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="climap.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='climap.js?v=8'></script>
EOM;

$t->content = <<<EOM

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<nav aria-label="breadcrumb">
<ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
        <li class="breadcrumb-item active" aria-current="page">Map of NWS Daily CLI Reports</li>
</ol>
</nav>

<div class="row">
<div class="col-12">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="mb-0">Map of NWS Daily CLI Reports</h4>
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
            <div class="col-md-2">
                <button id="dlcsv" class="btn btn-success w-100" type="button">
                    <i class="bi bi-download" aria-hidden="true"></i> CSV
                </button>
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

<div class="row">
<div class="col-12">
    <div class="card mt-4">
        <div class="card-header">
            <h5 class="card-title mb-0">CLI Report Details</h5>
            <small class="text-muted">Click on map markers to view detailed CLI text report</small>
        </div>
        <div class="card-body">
            <div id="clireport">
                <p class="text-muted mb-0">Click on a map location to view the CLI text report for that station.</p>
            </div>
        </div>
    </div>
</div>
</div>

EOM;

$t->render('full.phtml');
