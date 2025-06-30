<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 136);

require_once "../../include/myview.php";
require_once "../../include/forms.php";

$uri = "{$INTERNAL_BASEURL}/json/watches.py?is_pds=1";
$data = file_get_contents($uri);
$json = json_decode($data, $assoc = TRUE);
$table = "";
foreach ($json['events'] as $key => $val) {
    $spclink = sprintf(
        '<a target="_blank" href="https://www.spc.noaa.gov/products/watch/' .
            '%s/ww%04.0f.html">%s %s</a>',
        $val['year'],
        $val['num'],
        $val["type"],
        $val['num']
    );
    $table .= sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $spclink,
        $val["states"],
        $val["issue"],
        $val["expire"],
        $val["tornadoes_1m_strong"],
        $val["hail_1m_2inch"],
        $val["max_hail_size"],
        $val["max_wind_gust_knots"],
    );
}

$t = new MyView();
$t->title = "Particularly Dangerous Situation SPC Watches Listing";

// Use Tabulator ES module and Bootstrap 5 for styling
$t->headextra = <<<EOM
<link href="https://cdn.jsdelivr.net/npm/tabulator-tables@5.5.3/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet">
<link type="text/css" href="pds_watches.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script type="module" src="pds_watches.module.js"></script>
EOM;

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb bg-light px-2 py-2 mb-3">
    <li class="breadcrumb-item"><a href="/nws/">NWS Resources</a></li>
    <li class="breadcrumb-item active" aria-current="page">Particularly Dangerous Situation Watches</li>
  </ol>
</nav>
<h1 class="mb-3">Particularly Dangerous Situation SPC Watches</h1>

<div class="alert alert-info mb-4">This page presents the current <strong>unofficial</strong> IEM accounting of SPC watches that contain the special Particularly Dangerous Situation phrasing.</div>

<div class="mb-3">
  There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can directly access it here:
  <br><code>{$EXTERNAL_BASEURL}/json/watches.py?is_pds=1</code>
</div>

<div class="mb-4">
  <strong>Related:</strong>
  <a class="btn btn-primary btn-sm me-2" href="/vtec/emergencies.php">TOR/FFW Emergencies</a>
  <a class="btn btn-primary btn-sm me-2" href="/nws/watches.php">List Watches by Year</a>
  <a class="btn btn-primary btn-sm" href="/vtec/pds.php">PDS Warnings</a>
</div>

<div class="card mb-4">
  <div class="card-body">
    <div id="pds-table"></div>
  </div>
</div>
EOM;
$t->render("full.phtml");
