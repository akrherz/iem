<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 142);
require_once "../../../include/myview.php";
require_once "../../../include/mlib.php";
require_once "../../../include/forms.php";

$t = new MyView();
$t->headextra = <<<EOM
<link href="https://unpkg.com/tabulator-tables@6.2.1/dist/css/tabulator.min.css" rel="stylesheet">
<link type="text/css" href="index.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="https://unpkg.com/luxon@3.4.4/build/global/luxon.min.js"></script>
<script src="index.module.js?v=5" type="module"></script>
EOM;

$state = isset($_REQUEST['state']) ? xssafe($_REQUEST['state']) : null;
$year = get_int404("year", date("Y"));
$opt = get_int404("opt", 0);

$t->title = "WPC National High Low Temperature";

$sselect = stateSelect($state);
$yselect = yearSelect(2008, $year);
$opts = Array(
    1 => "By State",
    0 => "By Year",
);
$oselect = make_select("opt", $opt, $opts);

// Prepare initial parameters for JavaScript
$initialParams = array();
if ($opt == 1 && $state) {
    $initialParams["state"] = $state;
    $title = "Entries for state: {$state}";
} else {
    $initialParams["year"] = $year;
    $title = "Entries for year: {$year}";
}

function write_entry($entry){
    return sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n",
        $entry["date"], $entry["N_val"],
        implode("<br />", $entry["N_names"]), $entry["X_val"],
        implode("<br />", $entry["X_names"]));
}

$yearselected = ($opt == 0) ? ' checked="checked" ': "";
$stateselected = ($opt == 1) ? ' checked="checked" ': "";
$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/nws/">NWS User Resources</a></li>
 <li class="breadcrumb-item active" aria-current="page">WPC National High Low</li>
</ol>
</nav>

<div class="d-flex align-items-center mb-4 page-header">
    <h1 class="mb-0 me-3 text-white">
        <i class="bi bi-thermometer-half me-2"></i>
        WPC National High/Low Temperature
    </h1>
    <div class="ms-auto">
        <span class="badge bg-light text-dark">
            <i class="bi bi-database me-1"></i>Since 2008
        </span>
    </div>
</div>

<div class="alert alert-info d-flex align-items-start mb-4 border-0">
    <i class="bi bi-info-circle-fill me-3 flex-shrink-0" style="font-size: 1.5rem; color: #0dcaf0;"></i>
    <div>
        <h6 class="alert-heading mb-2">
            <i class="bi bi-graph-up me-1"></i>About This Tool
        </h6>
        <p class="mb-2">The IEM maintains an archive of the <a href="https://www.wpc.ncep.noaa.gov/discussions/hpcdiscussions.php?disc=nathilo&version=0&fmt=reg" target="_blank" class="alert-link">National High and Low Temperature</a>
        product. This product is disseminated over NOAAPort in XML format and called
        <a href="/wx/afos/p.php?pil=XTEUS" target="_blank" class="alert-link">XTEUS</a>.</p>
        <p class="mb-0">
            <strong><i class="bi bi-calendar-range me-1"></i>Data Range:</strong> Archive begins on <strong>30 June 2008</strong>. Data quality prior to 2011 may be suspect due to raw text product issues.
            <br><strong><i class="bi bi-api me-1"></i>API Access:</strong> Powered by an <a href="/api/1/docs#/nws/service_nws_wpc_national_hilo__fmt__get" target="_blank" class="alert-link">IEM Web Service</a>.
        </p>
    </div>
</div>

<div class="row mb-4">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header bg-light">
                <h5 class="card-title mb-0">
                    <i class="bi bi-sliders me-2"></i>Filter Options
                </h5>
            </div>
            <div class="card-body">
                <form method="GET" name="changeme" id="filter-form">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="opt" value="0" {$yearselected} id="year">
                                <label class="form-check-label fw-semibold" for="year">
                                    <i class="bi bi-calendar-event me-1"></i>Select by Year
                                </label>
                            </div>
                            <div class="mt-2">
                                {$yselect}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="opt" value="1" {$stateselected} id="state">
                                <label class="form-check-label fw-semibold" for="state">
                                    <i class="bi bi-geo-alt me-1"></i>Select by State
                                </label>
                            </div>
                            <div class="mt-2">
                                {$sselect}
                                <div class="form-text">Only contiguous US States</div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="bi bi-arrow-clockwise me-2"></i>Update Table
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
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
                        <strong>Choose Filter:</strong> Select by year or state
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-2-circle-fill text-primary me-2"></i>
                        <strong>Update Data:</strong> Click "Update Table" to refresh
                    </li>
                    <li class="mb-2">
                        <i class="bi bi-3-circle-fill text-primary me-2"></i>
                        <strong>Interactive Table:</strong> Sort, filter, and export data
                    </li>
                    <li class="mb-0">
                        <i class="bi bi-4-circle-fill text-primary me-2"></i>
                        <strong>Export Options:</strong> Download data in multiple formats
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <h5 class="card-title mb-0">
                    <i class="bi bi-table me-2"></i>{$title}
                    <span id="result-count" class="badge bg-light text-dark ms-2">Loading...</span>
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
                <div id="data-table"></div>
                <div id="loading-indicator" class="d-none position-absolute top-50 start-50 translate-middle">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script type="application/json" id="initial-params">
<?php echo json_encode($initialParams); ?>
</script>

<script type="application/json" id="page-title">
<?php echo json_encode($title); ?>
</script>

EOM;
$t->render('full.phtml');
