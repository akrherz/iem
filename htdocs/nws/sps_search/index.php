<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 140);
require_once "../../../include/mlib.php";
force_https();
require_once "../../../include/myview.php";
require_once "../../../include/iemprop.php";
$t = new MyView();
$OL = "10.6.1";

$t->jsextra = <<<EOM
<script src='https://unpkg.com/tabulator-tables@6.2.1/dist/js/tabulator.min.js'></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script type="text/javascript" src="/js/olselect-lonlat.js"></script>
<script type="text/javascript" src="index.js?v=6"></script>
EOM;

$t->headextra = <<<EOM
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator.min.css" rel="stylesheet">
<link rel="stylesheet" href="index.css" type='text/css'>
EOM;
$t->title = "Special Weather Statement (SPS) Search by Point";

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
<li class="breadcrumb-item active" aria-current="page">SPS Search by Point</li>
</ol>
</nav>

<div class="d-flex align-items-center mb-4 page-header px-4 py-3">
    <h1 class="mb-0 me-3 text-white">
        <i class="bi bi-geo-alt-fill me-2"></i>
        Special Weather Statement Search
    </h1>
    <div class="ms-auto">
        <span class="badge bg-light text-dark">
            <i class="bi bi-lightning-charge me-1"></i>Real-time Data
        </span>
    </div>
</div>

<div class="alert alert-info d-flex align-items-start mb-4 border-0">
    <i class="bi bi-info-circle-fill me-3 flex-shrink-0" style="font-size: 1.5rem; color: #0dcaf0;"></i>
    <div>
        <h6 class="alert-heading mb-2">
            <i class="bi bi-search me-1"></i>About This Tool
        </h6>
        <p class="mb-2">Search NWS Special Weather Statements (SPS) that contained a polygon for a specific location and time period.
        Only SPS products with geographic polygons are included in this search.</p>
        <p class="mb-0">
            <strong><i class="bi bi-cursor me-1"></i>How to use:</strong> Either drag the map marker or enter coordinates manually, then select your date range to search for relevant SPS products.
        </p>
    </div>
</div>

<div class="row mb-4">
    <div class="col-auto">
        <a class="btn btn-primary btn-lg" href="/request/gis/sps.phtml">
            <i class="bi bi-download me-2"></i>SPS Download
        </a>
    </div>
    <div class="col-auto">
        <a class="btn btn-outline-primary btn-lg" href="/wx/afos/p.php?pil=SPSDMX">
            <i class="bi bi-file-text me-2"></i>SPS Text Download
        </a>
    </div>
    <div class="col-auto ms-auto">
        <div class="text-muted small">
            <i class="bi bi-clock me-1"></i>Last updated: <span id="last-update">Loading...</span>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-4">
        <div class="card h-100">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="bi bi-sliders me-2"></i>Search Parameters
                </h5>
            </div>
            <div class="card-body">
                <div class="mb-4 coordinates-section">
                    <h6 class="text-primary mb-3 fw-bold">
                        <i class="bi bi-crosshair me-2"></i>Coordinates
                    </h6>
                    <div class="row g-3 mb-3">
                        <div class="col-6">
                            <label for="lat" class="form-label small fw-semibold">
                                <i class="bi bi-arrow-up me-1"></i>Latitude (°N)
                            </label>
                            <input type="number" class="form-control form-control-lg" id="lat" value="41.53" step="0.0001" min="-90" max="90" placeholder="41.53">
                        </div>
                        <div class="col-6">
                            <label for="lon" class="form-label small fw-semibold">
                                <i class="bi bi-arrow-right me-1"></i>Longitude (°E)
                            </label>
                            <input type="number" class="form-control form-control-lg" id="lon" value="-93.653" step="0.0001" min="-180" max="180" placeholder="-93.653">
                        </div>
                    </div>
                    <button type="button" class="btn btn-outline-primary btn-lg w-100" id="manualpt">
                        <i class="bi bi-geo-alt me-2"></i>Update Location
                    </button>
                </div>
                
                <div class="mb-4">
                    <h6 class="text-primary mb-3 fw-bold">
                        <i class="bi bi-calendar-range me-2"></i>Date Range
                    </h6>
                    <div class="mb-3">
                        <label for="sdate" class="form-label small fw-semibold">
                            <i class="bi bi-calendar-event me-1"></i>Start Date
                        </label>
                        <input name="sdate" type="date" id="sdate" class="form-control form-control-lg">
                    </div>
                    <div class="mb-3">
                        <label for="edate" class="form-label small fw-semibold">
                            <i class="bi bi-calendar-check me-1"></i>End Date
                        </label>
                        <input name="edate" type="date" id="edate" class="form-control form-control-lg">
                    </div>
                </div>
                
                <div class="bg-light p-4 rounded-3 border">
                    <h6 class="text-primary mb-3 fw-bold">
                        <i class="bi bi-map me-2"></i>Interactive Map
                    </h6>
                    <p class="small text-muted mb-3">
                        <i class="bi bi-hand-index me-1"></i>Drag the marker to select coordinates
                    </p>
                    <div id="map" class="map"></div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-8">
        <div class="card h-100 shadow-sm">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0" id="table1title">
                    <i class="bi bi-table me-2"></i>SPS Results
                    <span id="result-count" class="badge bg-light text-dark ms-2">0</span>
                </h5>
                <div class="btn-group" role="group">
                    <button type="button" id="export-excel" class="btn btn-success">
                        <i class="bi bi-file-earmark-excel me-1"></i>Excel
                    </button>
                    <button type="button" id="export-csv" class="btn btn-outline-light">
                        <i class="bi bi-file-earmark-text me-1"></i>CSV
                    </button>
                </div>
            </div>
            <div class="card-body p-0">
                <div id="table1" class="position-relative"></div>
                <div id="loading-indicator" class="d-none position-absolute top-50 start-50 translate-middle">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

EOM;
$t->render('full.phtml');
