<?php
// Main landing page for the IEM Sites stuff
$OL = "10.6.1";
define("IEM_APPID", 5);
require_once "../../include/forms.php";
if (isset($_GET["station"]) && isset($_GET["network"])) {
    $uri = sprintf(
        "site.php?station=%s&network=%s",
        xssafe($_REQUEST["station"]),
        xssafe($_REQUEST["network"])
    );
    header("Location: $uri");
    exit();
}
require_once "../../include/mlib.php";
force_https();
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS";

$t = new MyView();
$t->iemselect2 = TRUE;
$t->title = "Site Locator";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.js"></script>
EOM;

$nselect = selectNetwork($network);
$n2select = networkSelect($network, "");

$t->content = <<<EOM
<div class="row">
    <div class="col-12">
        <div class="d-flex align-items-center mb-4">
            <i class="bi bi-geo-alt-fill fs-1 text-primary me-3"></i>
            <div>
                <h1 class="mb-1">IEM Site Information</h1>
                <p class="text-muted mb-0">Locate and explore weather monitoring stations</p>
            </div>
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-12">
        <div class="alert alert-info" role="alert">
            <i class="bi bi-info-circle me-2"></i>
            <strong>About this tool:</strong> The IEM collects information from many sites organized into 
            networks based on their geography and/or the organization who administers the network. 
            This application provides metadata and site-specific applications you may find useful.
        </div>
    </div>
</div>

<div class="row mb-4">
    <div class="col-lg-6 mb-3">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-diagram-3 me-2"></i>Select By Network
            </div>
            <div class="card-body">
                <form name="switcher" class="d-flex gap-2">
                    <div class="flex-grow-1">
                        {$nselect}
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-arrow-left-right me-1"></i>Switch Network
                    </button>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-lg-6 mb-3">
        <div class="card">
            <div class="card-header bg-success text-white">
                <i class="bi bi-geo-alt me-2"></i>Select By Station
            </div>
            <div class="card-body">
                <form name="olselect">
                    <input type="hidden" name="network" value="{$network}">
                    <div class="d-flex gap-2">
                        <div class="flex-grow-1">
                            {$n2select}
                        </div>
                        <button type="submit" class="btn btn-success">
                            <i class="bi bi-check-lg me-1"></i>Select Station
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                <div>
                    <i class="bi bi-map me-2"></i>Interactive Station Map
                </div>
                <div class="d-flex gap-3">
                    <span class="badge bg-success">
                        <i class="bi bi-circle-fill me-1"></i>Online
                    </span>
                    <span class="badge bg-warning text-dark">
                        <i class="bi bi-circle-fill me-1"></i>Offline
                    </span>
                </div>
            </div>
            <div class="card-body p-0">
                <div class="alert alert-light border-0 rounded-0 mb-0">
                    <small class="text-muted">
                        <i class="bi bi-lightbulb me-1"></i>
                        <strong>Tip:</strong> Green dots represent stations online with current data. 
                        Yellow dots are stations that are no longer active. Click on a dot to select a station.
                    </small>
                </div>
                <div id="map" style="width:100%; height: 500px; border-radius: 0 0 0.375rem 0.375rem;" data-network="{$network}"></div>
            </div>
        </div>
    </div>
</div>
EOM;
$t->render('single.phtml');
