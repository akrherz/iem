<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 120);
$OL = "10.6.1";

require_once "../../include/myview.php";
require_once "../../include/forms.php";

$t = new MyView();
$t->title = "Tornado + Flash Flood Emergencies Listing";
$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="emergencies.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="emergencies.js"></script>
EOM;


$t->content = <<<EOM
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
                    <li class="breadcrumb-item active" aria-current="page">Tornado + Flash Flood Emergencies</li>
                </ol>
            </nav>
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <h3>NWS Tornado + Flash Flood Emergencies</h3>
            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading"><i class="bi bi-info-circle"></i> About Emergency Warnings</h4>
                <p>This page presents the current <strong>unofficial</strong> IEM accounting of Tornado and Flash Flood Emergencies issued by the NWS. If you find any discrepancies, please <a href="/info/contacts.php" class="alert-link">let us know</a>!</p>
                <hr>
                <p class="mb-0">You may wonder how events prior to the implementation of VTEC have eventids. These were retroactively generated and assigned by the IEM.</p>
            </div>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-md-6">
            <div class="alert alert-secondary" role="alert">
                <h6 class="alert-heading"><i class="bi bi-link-45deg"></i> External Resources</h6>
                <p class="mb-2">Link to <a href="https://en.wikipedia.org/wiki/List_of_United_States_tornado_emergencies" class="alert-link" target="_blank">Wikipedia List of United States tornado emergencies</a></p>
                <p class="mb-0">Data available via <a href="/api/1/docs#/vtec/service_nws_emergencies__fmt__get" class="alert-link">IEM webservice</a>: <code>{$EXTERNAL_BASEURL}/api/1/nws/emergencies.geojson</code></p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="alert alert-primary" role="alert">
                <h6 class="alert-heading"><i class="bi bi-collection"></i> Related Resources</h6>
                <div class="d-flex gap-2 flex-wrap">
                    <a class="btn btn-sm btn-outline-primary" href="/vtec/pds.php">PDS Warnings</a>
                    <a class="btn btn-sm btn-outline-primary" href="/nws/pds_watches.php">SPC PDS Watches</a>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0"><i class="bi bi-calendar-date"></i> Date Filter</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label for="startdate" class="form-label">Start Date:</label>
                            <input type="date" class="form-control" id="startdate" />
                        </div>
                        <div class="col-md-4">
                            <label for="enddate" class="form-label">End Date:</label>
                            <input type="date" class="form-control" id="enddate" />
                        </div>
                        <div class="col-md-4 d-flex align-items-end">
                            <button class="btn btn-primary" id="applyFilter">
                                <i class="bi bi-funnel"></i> Apply Filter
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-12">
            <h4 id="filter-title" class="text-muted"></h4>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-success text-white">
                    <h5 class="card-title mb-0"><i class="bi bi-geo-alt"></i> Interactive Map</h5>
                </div>
                <div class="card-body p-0">
                    <div id="map" style="height: 400px;"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-info text-white">
                    <h5 class="card-title mb-0"><i class="bi bi-table"></i> Emergency Events Data</h5>
                </div>
                <div class="card-body">
                    <div id="thetable">
                        <div id="emergencies-table"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

EOM;
$t->render("full.phtml");
