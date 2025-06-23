<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
define("IEM_APPID", 115);
$year = get_int404("year", intval(date("Y")));

require_once "../../include/myview.php";

$uri = sprintf("%s/json/vtec_max_etn.py?year=%s&format=html", 
    $INTERNAL_BASEURL,
    $year);
$wsuri = sprintf("%s/json/vtec_max_etn.py?year=%s",
    $EXTERNAL_BASEURL,
    $year);
$table = file_get_contents($uri);

$t = new MyView();
$t->title = "VTEC Event Listing for $year";
$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link type="text/css" href="maxetn.css" rel="stylesheet" />
EOM;

$yselect = yearSelect(2005, $year, 'year');

$t->content = <<<EOM
<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
                <li class="breadcrumb-item active" aria-current="page">Max VTEC EventID Listing</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="alert alert-info" role="alert">
            <h4 class="alert-heading"><i class="bi bi-info-circle"></i> About VTEC Event Tracking</h4>
            <p>The National Weather Service uses a system called
            <a href="http://www.nws.noaa.gov/om/vtec/" class="alert-link">Valid Time Event Code (VTEC)</a> to provide
            more accurate tracking of its watch, warning, and advisories. The IEM attempts to provide a
            high fidelity database of these products.</p>
            <hr>
            <p class="mb-0">The following table shows the largest VTEC eventids (ETN) for each NWS Forecast Office, 
            each phenomena, and significance for the given year. <strong>Pro-tip</strong>: Use the search functionality 
            to filter by a specific WFO.</p>
        </div>
    </div>
</div>

<div class="row mb-3">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0"><i class="bi bi-calendar-event"></i> Year Selection</h5>
            </div>
            <div class="card-body">
                <form method="GET" action="maxetn.php" class="d-flex gap-2 align-items-end">
                    <div class="flex-grow-1">
                        <label for="year" class="form-label">Select Year:</label>
                        $yselect
                    </div>
                    <div>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-arrow-clockwise"></i> Update Table
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="card-title mb-0"><i class="bi bi-api"></i> JSON API</h5>
            </div>
            <div class="card-body">
                <p class="card-text">This data is available via our <a href="/json/">JSON Webservice</a>:</p>
                <div class="input-group">
                    <input type="text" class="form-control font-monospace" value="{$wsuri}" readonly>
                    <button class="btn btn-outline-secondary" type="button" onclick="navigator.clipboard.writeText('{$wsuri}')">
                        <i class="bi bi-clipboard"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h3 class="card-title mb-0">Max VTEC ETN Listing for {$year}</h3>
                <div class="btn-group" role="group" id="download-buttons" style="display: none;">
                    <button type="button" class="btn btn-success btn-sm" id="download-csv">
                        <i class="bi bi-file-earmark-spreadsheet"></i> Download CSV
                    </button>
                    <button type="button" class="btn btn-secondary btn-sm" id="copy-clipboard">
                        <i class="bi bi-clipboard"></i> Copy to Clipboard
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div id="loading-indicator" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading VTEC data...</p>
                </div>
                <div id="vtec-table" style="display: none;"></div>
                <div id="error-message" class="alert alert-danger" role="alert" style="display: none;">
                    <i class="bi bi-exclamation-triangle"></i> Error loading data. Please try again.
                </div>
            </div>
        </div>
    </div>
</div>

EOM;
$t->jsextra = <<<EOM
<script src="maxetn.module.js" type="module"></script>
EOM;
$t->render("full.phtml");
