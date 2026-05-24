<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 2);
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/network.php";

$OL = "10.9.0";
$t = new MyView();
$t->title = "NWS COOP Daily Climatology";

// Get URL parameters with defaults
$tbl = substr(get_str404("tbl", "climate"), 0, 10);
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$sortcol = get_str404("sortcol", "station");
$network = substr(get_str404("network", "IACLIMATE"), 0, 9);
$station = get_str404("station", null);
$sortdir = get_str404("sortdir", "ASC");

// Build render variables array
$render_vars = array(
    'tbl' => $tbl,
    'month' => $month,
    'day' => $day,
    'sortcol' => $sortcol,
    'network' => $network,
    'station' => $station,
    'sortdir' => $sortdir
);

// Create form selects
$netselect = selectNetworkType("CLIMATE", $network);
$mselect = monthSelect($month, "month");
$dselect = daySelect($day, "day");

$ar = array(
    "climate" => "All Available",
    "climate51" => "Since 1951",
    "climate71" => "1971-2000",
    "climate81" => "1981-2010"
);
$tblselect = make_select("tbl", $tbl, $ar);


$t->content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb small mb-3">
        <li class="breadcrumb-item"><a href="/COOP/">NWS COOP</a></li>
        <li class="breadcrumb-item active" aria-current="page">Daily Climatology</li>
    </ol>
</nav>

<header class="mb-4">
    <h1 class="h3 mb-2">NWS COOP Daily Climatology</h1>
    <p class="mb-0 text-body-secondary">Explore daily climate records by state and date, then switch into a station view to compare one station across the full calendar year.</p>
</header>

<div id="loading-indicator" class="text-center my-4 d-none" aria-live="polite">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading climatology data</span>
    </div>
    <p class="mt-2 mb-0">Loading climatology data...</p>
</div>

<div id="content-area">
    <div id="header-section">
        <!-- Header will be populated by JavaScript -->
    </div>

    <div class="alert alert-info shadow-sm border-0">
        <h2 class="h5 alert-heading">Two App Modes Available</h2>
        <div class="row">
            <div class="col-md-6">
                <strong>Single Date Climatology for State</strong>
                <p class="mb-0 small">Select a specific date to see records for all stations on that day. Use the form below to choose date and state.</p>
            </div>
            <div class="col-md-6">
                <strong>Daily Climatology for Single Station</strong>
                <p class="mb-0 small">Click any station ID in the table to see all daily records for that station throughout the year.</p>
            </div>
        </div>
    </div>

    <p>This table gives a listing of <b>unofficial</b> daily records for NWS
    COOP stations. You may click on a column to sort it.  You can click on the station
    name to get all daily records for that station or click on the date to get all records
    for that date.</p>

    <p><a href="/COOP/dl/normals.phtml" class="btn btn-primary">
    <i class="bi bi-download" aria-hidden="true"></i> Download Daily Climatology</a></p>

    <div id="api-info" class="alert alert-light border shadow-sm d-none">
        <p class="mb-0">The data found in this table was derived from the following
        <a href="/json/">JSON webservice</a>:<br />
        <code id="api-url"></code>
        </p>
    </div>

    <form method="GET" action="extremes.php" name="myform" id="controls-form">
    <div class="card shadow-sm border-0 mb-4">
        <div class="card-header">
            <h2 class="h6 mb-0">Single Date Mode Controls</h2>
            <small class="text-muted">Change state or date to view different climatology data</small>
        </div>
        <div class="card-body p-3">
            <div class="row g-2 align-items-end">
                <div class="col-md-3">
                    <label for="network" class="form-label small">Select State:</label>
                    {$netselect}
                </div>
                <div class="col-md-3">
                    <label class="form-label small">Select Date:</label>
                    <div class="d-flex gap-1">
                        {$mselect} {$dselect}
                    </div>
                </div>
                <div class="col-md-3">
                    <label for="tbl" class="form-label small">Record Database:</label>
                    {$tblselect}
                </div>
                <div class="col-md-3">
                    <input type="submit" value="Update Data" class="btn btn-primary btn-sm" id="form-submit-btn">
                    <div id="dynamic-indicator" style="display: none; font-size: 11px; color: #666; margin-top: 4px;">
                        Changes update automatically
                    </div>
                </div>
            </div>
        </div>
    </div>
    </form>

    <!-- Map Container (only visible for all stations mode) -->
    <section id="map-container" class="card shadow-sm border-0 mb-4">
        <div class="card-header bg-body-tertiary border-0">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-2 align-items-lg-center">
                <div>
                    <h2 class="h5 mb-1">Station Map</h2>
                    <p class="small text-body-secondary mb-0">Choose a map label, filter extreme-year records, and click a station for full daily-climatology details.</p>
                </div>
                <div class="small text-body-secondary">Use the layer switcher in the upper-right corner to change basemaps.</div>
            </div>
        </div>
        <div class="card-body">
            <div class="map-toolbar row g-3 align-items-end mb-3">
                <div class="col-md-5 col-xl-4">
                    <label for="label-attribute" class="form-label small mb-1">Label Points With</label>
                    <select id="label-attribute" class="form-select form-select-sm">
                        <option value="station">Station ID</option>
                        <option value="avg_high" selected>Avg High</option>
                        <option value="max_high">Max High</option>
                        <option value="min_high">Min High</option>
                        <option value="avg_low">Avg Low</option>
                        <option value="max_low">Max Low</option>
                        <option value="min_low">Min Low</option>
                        <option value="avg_precip">Avg Precip</option>
                        <option value="max_precip">Max Precip</option>
                        <option value="years">Years</option>
                    </select>
                </div>
                <div class="col-md-4 col-xl-3">
                    <label for="year-filter" class="form-label small mb-1">Filter by Record Year</label>
                    <select id="year-filter" class="form-select form-select-sm">
                        <option value="">All Years</option>
                        <!-- Options populated dynamically -->
                    </select>
                </div>
                <div class="col-md-3 col-xl-5">
                    <div class="small text-uppercase text-body-secondary mb-1">Legend</div>
                    <div class="map-legend rounded border bg-light-subtle p-2">
                        <!-- Legend will be populated dynamically by JavaScript -->
                    </div>
                </div>
            </div>
            <div class="map-stage">
                <div id="map" class="map-canvas" role="region" aria-label="Climate station map"></div>
                <div id="popup" class="ol-popup">
                    <a href="#" id="popup-closer" class="ol-popup-closer" aria-label="Close station details"></a>
                    <div id="popup-content" class="ol-popup-content"></div>
                </div>
            </div>
        </div>
    </section>

    <section class="card shadow-sm border-0">
        <div class="card-header bg-body-tertiary border-0">
            <h2 class="h5 mb-0">Climatology Table</h2>
        </div>
        <div class="card-body p-0">
            <div class="table-responsive">
                <div id="data-table"></div>
            </div>
        </div>
    </section>
</div>
EOM;
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" type="text/css">
<link rel="stylesheet" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" type="text/css">
<link rel="stylesheet" href="extremes.css" type="text/css">
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js"></script>
<script src="/vendor/openlayers/{$OL}/ol-layerswitcher.js"></script>
<script src="https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js"></script>
<script src="extremes.js?v=2" type="text/javascript"></script>
EOM;
$t->render('full.phtml');
