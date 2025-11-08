<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 85);
require_once "../../include/myview.php";
require_once "../../include/reference.php";
require_once "../../include/forms.php";
$vtec_phenomena = $reference["vtec_phenomena"];
$vtec_significance = $reference["vtec_significance"];
$wfo = substr(get_str404("wfo", 'DMX'), 0, 4);
$year = get_int404("year", intval(date("Y")));
$state = substr(get_str404('state', 'IA'), 0, 2);
$which = get_str404("which", 'wfo');
$significance = get_str404("s", "");
$phenomena = get_str404("p", "");
$pon = (get_str404("pon", null) == "on");
$son = (get_str404("son", null) == "on");


if ($which == 'wfo') {
    $service = "";
    $uri = sprintf(
        "%s/json/vtec_events.py?wfo=%s&year=%s",
        $INTERNAL_BASEURL,
        $wfo,
        $year
    );
} else {
    $service = "_bystate";
    $uri = sprintf(
        "%s/json/vtec_events_bystate.py?state=%s&year=%s",
        $INTERNAL_BASEURL,
        $state,
        $year
    );
}
if ($significance != "" && $son) {
    $uri .= sprintf("&significance=%s", $significance);
}
if ($phenomena != "" && $pon) {
    $uri .= sprintf("&phenomena=%s", $phenomena);
}
$public_uri = str_replace(
    $INTERNAL_BASEURL,
    $EXTERNAL_BASEURL,
    $uri
);

$t = new MyView();
if ($which == 'wfo') {
    $t->title = "VTEC Event Listing for $wfo during $year";
} else {
    $t->title = "VTEC Event Listing for $state during $year";
}
$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link type="text/css" href="events.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="events.module.js" type="module"></script>
EOM;
$yselect = yearSelect(2005, $year, 'year');
$wfoselect = networkSelect("WFO", $wfo, array(), "wfo");
$stselect = stateSelect($state);
$pselect = make_select("p", $phenomena, $vtec_phenomena);
$sselect = make_select("s", $significance, $vtec_significance);

$wchecked = ($which == 'wfo') ? "CHECKED" : "";
$schecked = ($which == 'state') ? "CHECKED" : "";
$ponchecked = $pon ? "CHECKED" : "";
$sonchecked = $son ? "CHECKED" : "";

$t->content = <<<EOM
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
                    <li class="breadcrumb-item active" aria-current="page">NWS VTEC Event Listing</li>
                </ol>
            </nav>
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <h3>NWS VTEC Event ID Usage</h3>
            <div class="alert alert-info" role="alert">
                <h4 class="alert-heading"><i class="bi bi-info-circle"></i> About VTEC Events</h4>
                <p>This page provides a listing of VTEC events for a given forecast office or state and year. There are a number of caveats to this listing due to issues encountered processing NWS VTEC enabled products. Some events may appear listed twice due to quirks with how this information is stored within the database.</p>
                <hr>
                <p class="mb-0">The "Event ID" column provides a direct link into the <a href="/vtec/" class="alert-link">IEM VTEC Browser</a> and the "HVTEC NWSLI" column provides a direct link into the <a href="/plotting/auto/?q=160" class="alert-link">HML Obs + Forecast Autoplot</a> application.</p>
            </div>
        </div>
    </div>

    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-filter"></i> Event Filters
                    </h5>
                </div>
                <div class="card-body">
                    <form method="GET" action="events.php" id="vtec-form">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <div class="card border">
                                    <div class="card-header bg-light">
                                        <h6 class="card-title mb-0">Search Scope</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="which" value="wfo" id="which-wfo" $wchecked>
                                                <label class="form-check-label" for="which-wfo">
                                                    <i class="bi bi-building"></i> By Weather Forecast Office
                                                </label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="which" value="state" id="which-state" $schecked>
                                                <label class="form-check-label" for="which-state">
                                                    <i class="bi bi-map"></i> By State
                                                </label>
                                            </div>
                                        </div>
                                        <div class="row g-2">
                                            <div class="col-6" id="wfo-select-container">
                                                <label for="wfo" class="form-label">WFO:</label>
                                                $wfoselect
                                            </div>
                                            <div class="col-6" id="state-select-container">
                                                <label for="state" class="form-label">State:</label>
                                                $stselect
                                            </div>
                                            <div class="col-6">
                                                <label for="year" class="form-label">Year:</label>
                                                $yselect
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-6">
                                <div class="card border">
                                    <div class="card-header bg-light">
                                        <h6 class="card-title mb-0">Event Type Filters</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="pon" value="on" id="pon" $ponchecked>
                                                <label class="form-check-label" for="pon">
                                                    <i class="bi bi-funnel"></i> Filter by Phenomena
                                                </label>
                                            </div>
                                            <div class="mt-2">
                                                $pselect
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="son" value="on" id="son" $sonchecked>
                                                <label class="form-check-label" for="son">
                                                    <i class="bi bi-funnel-fill"></i> Filter by Significance
                                                </label>
                                            </div>
                                            <div class="mt-2">
                                                $sselect
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="row mt-3">
                            <div class="col-12 text-center">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="bi bi-search"></i> Generate Event Listing
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <div class="row mb-3">
        <div class="col-md-8">
            <div class="alert alert-secondary" role="alert">
                <h6 class="alert-heading"><i class="bi bi-api"></i> JSON API Access</h6>
                <p class="mb-0">Data available via <a href="/json/" class="alert-link">JSON webservice</a>:</p>
                <div class="input-group mt-2">
                    <input type="text" class="form-control font-monospace" value="Loading..." readonly id="api-url">
                    <button class="btn btn-outline-secondary" type="button" onclick="navigator.clipboard.writeText('')">
                        <i class="bi bi-clipboard"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="btn-group w-100" role="group" id="download-buttons" style="display: none;">
                <button type="button" class="btn btn-success" id="download-csv">
                    <i class="bi bi-file-earmark-spreadsheet"></i> Download CSV
                </button>
                <button type="button" class="btn btn-secondary" id="copy-clipboard">
                    <i class="bi bi-clipboard"></i> Copy Data
                </button>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-table"></i> VTEC Events
                    </h5>
                    <span class="badge bg-light text-dark" id="event-count">Loading...</span>
                </div>
                <div class="card-body">
                    <div id="loading-indicator" class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading events...</span>
                        </div>
                        <p class="mt-2">Loading VTEC events...</p>
                    </div>
                    <div id="vtec-table" style="display: none;"></div>
                    <div id="error-message" class="alert alert-danger" role="alert" style="display: none;">
                        <i class="bi bi-exclamation-triangle"></i> Error loading events. Please try again.
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

EOM;
$t->render("single.phtml");
