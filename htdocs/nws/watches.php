<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 137);

require_once "../../include/myview.php";
require_once "../../include/forms.php";

$year = get_int404("year", date("Y"));
$uri = sprintf("%s/json/watches.py?year=%s", $INTERNAL_BASEURL, $year);
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
        "<tr><td>%s</td><td>%s%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $spclink,
        ($val["is_pds"]) ? ' <span class="badge bg-danger">PDS</span>' : "",
        $val["states"],
        $val["issue"],
        $val["expire"],
        $val["tornadoes_1m_strong"],
        $val["hail_1m_2inch"],
        $val["max_hail_size"],
        $val["max_wind_gust_knots"],
    );
}
// Create year select with Bootstrap 5 classes
$yearOptions = array();
for ($i = 1997; $i <= intval(date("Y")); $i++) {
    $yearOptions[$i] = (string)$i;
}
$yearselect = make_select("year", $year, $yearOptions, "", "form-select");
$t = new MyView();
$t->title = "SPC Watches Listing";
$t->headextra = <<<EOM
<link type="text/css" href="watches.css" rel="stylesheet" />
<link rel="stylesheet" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css">
EOM;
$t->jsextra = <<<EOM
<script src="watches.module.js" type="module"></script>
EOM;

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item">
      <a href="/nws/"><i class="bi bi-arrow-left-circle me-1"></i>NWS Resources</a>
    </li>
    <li class="breadcrumb-item active" aria-current="page">SPC Watch Listing</li>
  </ol>
</nav>

<div class="d-flex align-items-center mb-4">
  <i class="bi bi-shield-exclamation me-2 text-warning fs-4"></i>
  <h3 class="mb-0">Yearly Listing of SPC Watches</h3>
</div>

<div class="row mb-4">
  <div class="col-lg-8">
    <div class="alert alert-info d-flex align-items-start" role="alert">
      <i class="bi bi-info-circle-fill me-2 mt-1 flex-shrink-0"></i>
      <div>
        <strong>JSON API Available:</strong> This table is backed by a JSON webservice that you can access directly:
        <br><code class="mt-1 d-block">{$EXTERNAL_BASEURL}/json/watches.py?year=$year</code>
        <small class="text-muted mt-1 d-block">
          <i class="bi bi-link-45deg me-1"></i>
          Visit our <a href="/json/" class="alert-link">JSON(P) webservice documentation</a> for more details.
        </small>
      </div>
    </div>
  </div>
  <div class="col-lg-4">
    <div class="card">
      <div class="card-header bg-light">
        <h6 class="card-title mb-0">
          <i class="bi bi-link-45deg me-1"></i>Related Resources
        </h6>
      </div>
      <div class="card-body">
        <a class="btn btn-primary d-block" href="/nws/pds_watches.php">
          <i class="bi bi-exclamation-triangle-fill me-1"></i>PDS Watches
        </a>
      </div>
    </div>
  </div>
</div>

<div class="card mb-4">
  <div class="card-header bg-light">
    <h5 class="card-title mb-0">
      <i class="bi bi-funnel me-2"></i>Filter Options
    </h5>
  </div>
  <div class="card-body">
    <form method="GET" action="/nws/watches.php" name="ys">
      <div class="row g-3 align-items-end">
        <div class="col-md-6">
          <label for="year" class="form-label">
            <i class="bi bi-calendar me-1"></i>Select Year
          </label>
          $yearselect
        </div>
        <div class="col-md-6">
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-arrow-clockwise me-1"></i>Update Table
          </button>
        </div>
      </div>
    </form>
  </div>
</div>

<div class="card">
  <div class="card-header bg-primary text-white">
    <h5 class="card-title mb-0">
      <i class="bi bi-table me-2"></i>SPC Watches for $year
    </h5>
  </div>
  <div class="card-body p-0">
    <table id="watchesTable" class="table table-striped table-hover mb-0">
      <thead class="table-dark">
        <tr>
          <th><i class="bi bi-calendar-date me-1"></i>Year</th>
          <th><i class="bi bi-shield-check me-1"></i>Watch Num</th>
          <th><i class="bi bi-geo-alt me-1"></i>State(s)</th>
          <th><i class="bi bi-clock me-1"></i>Issued</th>
          <th><i class="bi bi-clock-history me-1"></i>Expired</th>
          <th><i class="bi bi-tornado me-1"></i>Prob EF2+ Tor</th>
          <th><i class="bi bi-cloud-hail me-1"></i>Prob Hail 2+in</th>
          <th><i class="bi bi-rulers me-1"></i>Max Hail Size</th>
          <th><i class="bi bi-wind me-1"></i>Max Wind Gust kts</th>
        </tr>
      </thead>
      <tbody>
        {$table}
      </tbody>
    </table>
  </div>
</div>

EOM;
$t->render("full.phtml");
