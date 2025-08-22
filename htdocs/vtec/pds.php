<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 122);

require_once "../../include/myview.php";
require_once "../../include/reference.php";
require_once "../../include/forms.php";
$vtec_phenomena = $reference["vtec_phenomena"];
$vtec_significance = $reference["vtec_significance"];

$uri = "{$INTERNAL_BASEURL}/json/vtec_pds.py";
$data = file_get_contents($uri);
$json = json_decode($data, $assoc = TRUE);
$table = "";
foreach ($json['events'] as $key => $val) {
    $table .= sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td>" .
            "<td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $val["wfo"],
        $val["states"],
        $val["uri"],
        $val["eventid"],
        $val["phenomena"],
        $val["significance"],
        $vtec_phenomena[$val["phenomena"]],
        $vtec_significance[$val["significance"]],
        $val["issue"],
        $val["expire"]
    );
}

$t = new MyView();
$t->title = "Particularly Dangerous Situation (PDS) Listing";
$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link type="text/css" href="pds.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script type="module" src="pds.module.js?v=3"></script>
EOM;


$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
 <li class="breadcrumb-item active" aria-current="page">PDS List</li>
</ol>
</nav>
<h1 class="h4 mb-3">Particularly Dangerous Situation Watch / Warnings</h1>
<div>

<p>This page presents the current and
<strong>unofficial</strong> IEM
accounting of watches/warnings that contain the special
Particularly Dangerous Situation
phrasing. This phrasing is the only key used to identify such events.
The phrasing can occur in either the issuance and/or followup statements.</p>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>{$EXTERNAL_BASEURL}/json/vtec_pds.py</code></p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/vtec/emergencies.php">TOR/FFW Emergencies</a>
<a class="btn btn-primary ms-2" href="/nws/pds_watches.php">SPC PDS Watches</a></p>

<p>
This listing was generated at: <code>{$json['generated_at']}</code> and is
regenerated hourly. <button id="makefancy" class="btn btn-success" aria-controls="pds-tabulator-table pds-status" aria-expanded="false">Make Table Interactive</button></p>

<div id="pds-status" class="visually-hidden" role="status" aria-live="polite"></div>

<!-- Tabulator Table Controls (hidden initially) -->
<div id="table-controls" class="d-none" aria-hidden="true">
    <div class="d-flex flex-wrap align-items-center">
        <div class="btn-group me-3 mb-2" role="group" aria-label="Download data">
            <button id="download-csv" type="button" class="btn btn-outline-primary">
                <i class="bi bi-download" aria-hidden="true"></i> CSV
            </button>
            <button id="download-json" type="button" class="btn btn-outline-primary">
                <i class="bi bi-download" aria-hidden="true"></i> JSON
            </button>
        </div>
        <div class="btn-group me-3 mb-2" role="group" aria-label="Utility actions">
            <button id="copy-clipboard" type="button" class="btn btn-outline-secondary">
                <i class="bi bi-clipboard" aria-hidden="true"></i> Copy
            </button>
            <button id="clear-filters" type="button" class="btn btn-outline-warning">
                <i class="bi bi-funnel" aria-hidden="true"></i> Clear Filters
            </button>
        </div>
    </div>
</div>

<!-- Modern Tabulator Table (hidden initially) -->
<div id="tabulator-container" class="d-none" aria-label="Interactive PDS events data table">
    <div id="pds-tabulator-table"></div>
</div>

<!-- Original Table (shown initially) -->
<div id="original-table">
<table class="table table-striped table-sm" id="pds-table">
<caption class="text-start">Listing of PDS (Particularly Dangerous Situation) watch and warning events. PH = VTEC Phenomena, SIG = VTEC Significance.</caption>
<thead class="sticky">
<tr><th>Year</th><th>WFO</th><th>State(s)</th><th>Event ID</th>
<th>PH</th><th>SIG</th><th>Event</th><th>Issue</th><th>Expire</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>

EOM;
$t->render("full.phtml");
