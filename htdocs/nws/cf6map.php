<?php
// Produce a map of CF6 parsed data for a single day
require_once "../../config/settings.inc.php";
define("IEM_APPID", 131);
require_once "../../include/myview.php";
require_once "../../include/mlib.php";
force_https();
$t = new MyView();
$t->title = "Map of Daily NWS CF6 reports";
$OL = '10.6.1';
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="cf6table.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='cf6map.js?v=2'></script>
EOM;

$t->content = <<<EOM

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<nav aria-label="breadcrumb">
<ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
        <li class="breadcrumb-item active" aria-current="page">Map of NWS Daily CF6 Reports</li>
</ol>
</nav>

<div class="d-flex align-items-center mb-4 page-header">
    <h1 class="mb-0 me-3 text-white">
        <i class="bi bi-cloud-sun-fill me-2"></i>
        NWS Daily CF6 Climate Reports
    </h1>
    <div class="ms-auto">
        <span class="badge bg-light text-dark">
            <i class="bi bi-thermometer-half me-1"></i>Climate Data
        </span>
    </div>
</div>

<div class="alert alert-info d-flex align-items-start mb-4 border-0">
    <i class="bi bi-info-circle-fill me-3 flex-shrink-0" style="font-size: 1.5rem; color: #0dcaf0;"></i>
    <div>
        <h6 class="alert-heading mb-2">
            <i class="bi bi-graph-up me-1"></i>About This Tool
        </h6>
        <p class="mb-2">Interactive map displaying NWS CF6 (Climate Data) reports for weather stations across the United States.
        Select different meteorological variables and dates to explore climate patterns.</p>
        <p class="mb-0">
            <strong><i class="bi bi-cursor me-1"></i>How to use:</strong> Choose a variable and date, then click on any station marker to view detailed CF6 report data.
        </p>
    </div>
</div>
        
<div class="row mb-4">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="bi bi-sliders me-2"></i>Display Controls
                </h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label for="renderattr" class="form-label fw-semibold">
                            <i class="bi bi-list-ul me-1"></i>Variable to Display
                        </label>
                        <select id="renderattr" class="form-select form-select-lg">
                            <option value="high">High Temperature</option>
                            <option value="low">Low Temperature</option>
                            <option value="avg_temp">Average Temperature</option>
                            <option value="dep_temp">Average Temperature Departure</option>
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
                            <option value="wxcodes">Weather Codes</option>
                            <option value="gust_smph">Wind Gust</option>
                            <option value="gust_drct">Wind Gust Direction</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label for="datepicker" class="form-label fw-semibold">
                            <i class="bi bi-calendar-event me-1"></i>Select Date
                        </label>
                        <input type="date" id="datepicker" class="form-control form-control-lg">
                    </div>
                </div>
                
                <div class="mt-3">
                    <label class="form-label fw-semibold">
                        <i class="bi bi-fonts me-1"></i>Font Size Controls
                    </label>
                    <div class="btn-group w-100" role="group">
                        <button id="fminus" class="btn btn-outline-secondary" type="button">
                            <i class="bi bi-dash-lg me-1"></i>Smaller
                        </button>
                        <button id="fplus" class="btn btn-outline-secondary" type="button">
                            <i class="bi bi-plus-lg me-1"></i>Larger
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="bi bi-info-square me-2"></i>Quick Guide
                </h5>
            </div>
            <div class="card-body">
                <ul class="list-unstyled mb-0">
                    <li class="mb-2">
                        <i class="bi bi-1-circle-fill text-primary me-2"></i>
                        <strong>Select Variable:</strong> Choose the meteorological parameter to display
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-2-circle-fill text-primary me-2"></i>
                        <strong>Pick Date:</strong> Select any date from 2001 onwards
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-3-circle-fill text-primary me-2"></i>
                        <strong>Click Stations:</strong> Click map markers to view detailed reports
                    </li>
                    <li class="mb-0">
                        <i class="bi bi-4-circle-fill text-primary me-2"></i>
                        <strong>Adjust Text:</strong> Use font size controls for better readability
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="card-title mb-0">
                    <i class="bi bi-geo-alt-fill me-2"></i>Interactive Climate Map
                </h5>
            </div>
            <div class="card-body p-0">
                <div id="map" class="map">
                    <div id="popup"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="bi bi-file-text me-2"></i>CF6 Report Details
                    <small class="text-muted ms-2">Click on map stations to view reports</small>
                </h5>
            </div>
            <div class="card-body">
                <div id="cf6report" class="position-relative">
                    <div class="text-center text-muted py-4">
                        <i class="bi bi-cursor-fill display-4 text-muted mb-3"></i>
                        <p class="lead">Click on any station marker on the map above to display the full CF6 climate report</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

EOM;

$t->render('full.phtml');
