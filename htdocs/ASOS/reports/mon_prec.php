<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS";
$year = get_int404("year", date("Y"));

$netselect = selectNetworkType("ASOS", $network);
$yselect = yearSelect(2004, $year, "year");

define("IEM_APPID", 29);
$t = new MyView();
$t->title = "{$year} {$network} Monthly Precipitation";

$pgconn = iemdb("iem");
$nt = new NetworkTable($network);
$cities = $nt->table;

$stname = iem_pg_prepare($pgconn, <<<EOM
SELECT 
 id,
 sum(pday) as precip,
 extract(month from day) as month
FROM summary_{$year} s JOIN stations t ON (t.iemid = s.iemid)
WHERE
 network = $1
 and pday >= 0
GROUP by id, month
EOM
);
$rs = pg_execute($pgconn, $stname, array($network));
$data = array();
for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    if (!array_key_exists($row['id'], $data)) {
        $data[$row['id']] = array(
            null, null, null, null, null, null, null,
            null, null, null, null, null
        );
    }
    $data[$row["id"]][intval($row["month"]) - 1] = $row["precip"];
}
$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link type="text/css" href="mon_prec.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script type="module" src="mon_prec.module.js?v=2"></script>
EOM;

reset($data);
function friendly($val)
{
    if (is_null($val)) return "M";
    return sprintf("%.2f", $val);
}
$table = "";
foreach ($data as $key => $val) {
    $table .= sprintf(
        "<tr><td><a href=\"/sites/site.php?station=%s&network=%s\">%s</a></td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%.2f</td><td>%.2f</td>
  </tr>",
        $key,
        $network,
        $key,
        $cities[$key]["name"],
        friendly($val[0]),
        friendly($val[1]),
        friendly($val[2]),
        friendly($val[3]),
        friendly($val[4]),
        friendly($val[5]),
        friendly($val[6]),
        friendly($val[7]),
        friendly($val[8]),
        friendly($val[9]),
        friendly($val[10]),
        friendly($val[11]),
        array_sum(array_slice($val, 4, 4)),
        array_sum($val)
    );
}

$d = date("d M Y h a");
$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/ASOS/">ASOS Mainpage</a></li>
    <li class="breadcrumb-item active" aria-current="page">{$year} {$network} Precipitation Report</li>
</ol>
</nav>

<h1 class="h4 mb-3">{$year} {$network} Monthly Precipitation</h1>
<p>This table was generated at <strong>{$d}</strong> and is based on available ASOS data. <strong>No attempt was made to estimate missing data.</strong></p>

<form name="change" class="mb-4">
<div class="row align-items-end">
    <div class="col-md-4 mb-3">
        <label for="network" class="form-label">Network:</label>
        {$netselect}
    </div>
    <div class="col-md-4 mb-3">
        <label for="year" class="form-label">Year:</label>
        {$yselect}
    </div>
    <div class="col-md-4 mb-3">
        <button type="submit" class="btn btn-primary">Change Year</button>
    </div>
</div>
</form>

<div>
    <div class="d-flex justify-content-between align-items-center mb-3">
            <h2 class="h5 mb-0">Monthly Precipitation Data</h2>
            <button id="create-grid" type="button" class="btn btn-success" aria-controls="tabulator-container precip-status" aria-expanded="false">Make Table Interactive</button>
    </div>

    <div id="precip-status" class="mb-3 visually-hidden" role="status" aria-live="polite"></div>

<!-- Tabulator Table Controls (hidden initially) -->
<div id="table-controls" class="d-none" aria-hidden="true">
    <div class="d-flex flex-wrap align-items-center">
        <div class="btn-group me-3 mb-2" role="group" aria-label="Download data">
            <button id="download-csv" type="button" class="btn btn-outline-primary">
                <i class="bi bi-download" aria-hidden="true"></i> Download CSV
            </button>
            <button id="download-json" type="button" class="btn btn-outline-primary">
                <i class="bi bi-download" aria-hidden="true"></i> Download JSON
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
<div id="tabulator-container" class="d-none" aria-label="Interactive precipitation data table">
    <div id="precipitation-tabulator-table"></div>
</div>

<!-- Original Table (shown initially) -->
<div id="original-table">
<table class="table table-striped table-sm" id="datagrid">
<caption class="text-start">Monthly and seasonal (MJJA) precipitation totals (inches) for stations in the {$network} network, year {$year}. M denotes missing.</caption>
<thead class="sticky">
<tr>
<th>ID</th>
<th>Name</th>
<th>Jan</th>
<th>Feb</th>
<th>Mar</th>
<th>Apr</th>
<th>May</th>
<th>Jun</th>
<th>Jul</th>
<th>Aug</th>
<th>Sep</th>
<th>Oct</th>
<th>Nov</th>
<th>Dec</th>
<th><strong>MJJA</strong></th>
<th><strong>Year</strong></th>
</tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>
EOM;
$t->render('single.phtml');
