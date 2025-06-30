<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 141);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";

$t = new MyView();

$t->headextra = <<<EOM
<link type="text/css" href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator_bootstrap5.min.css" rel="stylesheet" />
<link type="text/css" href="list_ugcs.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="list_ugcs.module.js" type="module"></script>
EOM;

$wfo = isset($_REQUEST['station']) ? xssafe($_REQUEST['station']) : 'DMX';
$just_firewx = isset($_REQUEST["just_firewx"]) ? intval(xssafe($_REQUEST["just_firewx"])) : 0;
$w = isset($_REQUEST["w"]) ? xssafe($_REQUEST["w"]) : "wfo";
$state = isset($_REQUEST["state"]) ? xssafe($_REQUEST["state"]) : "IA";
if (($just_firewx != 1) && ($just_firewx != 0)){
    $just_firewx = 0;
}

$t->title = "NWS UGCs by WFO";

$wselect = networkSelect("WFO", $wfo);
$opts = Array(
    1 => "Just Fire Weather Zones",
    0 => "Show Non-Fire Weather Zones",
);
$fselect = make_select("just_firewx", $just_firewx, $opts);

$arr = array(
    "just_firewx" => $just_firewx,
);
$title = "";
if (($w == "wfo") && isset($_REQUEST["w"])) {
    $title = "for WFO: $wfo";
    $arr["wfo"] = $wfo;
}
else if ($w == "state") {
    $title = "for state: $state";
    $arr["state"] = $state;
}

$wfoselected = ($w == "wfo") ? 'checked="checked"': "";
$stateselected = ($w == "state") ? 'checked="checked"': "";
$sselect = stateSelect($state);

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb bg-light px-3 py-2 mb-4 rounded">
    <li class="breadcrumb-item"><a href="/nws/">NWS User Resources</a></li>
    <li class="breadcrumb-item active" aria-current="page">NWS UGCs by WFO</li>
  </ol>
</nav>

<div class="card ugcs-card">
  <div class="card-body">
    <p class="mb-2">The National Weather Service issues many products associated with
      <a href="https://www.weather.gov/gis/AWIPSShapefiles">Universal Geographic Codes</a> (UGCs).
      These UGCs represent counties, forecast zones, marine zones, or fire weather zones. This page lists out a current listing of such codes and is powered by an
      <a href="/api/1/docs#/nws/service_nws_ugcs__fmt__get">IEM Webservice</a>.
    </p>
    <p class="mb-0">The default display <a href="list_ugcs.php">lists all non-fire weather UGCs</a> or
      you can <a href="list_ugcs.php?just_firewx=1">list all fire weather UGCs</a>.
    </p>
  </div>
</div>

<form method="GET" name="changeme" class="row g-3 align-items-end mb-4 bg-white p-3 rounded shadow-sm">
  <div class="col-md-4">
    <div class="form-check mb-1">
      <input class="form-check-input" type="radio" name="w" value="wfo" {$wfoselected} id="wfo">
      <label class="form-check-label ugcs-form-label" for="wfo">Select by WFO</label>
    </div>
    {$wselect}
  </div>
  <div class="col-md-4">
    <div class="form-check mb-1">
      <input class="form-check-input" type="radio" name="w" value="state" {$stateselected} id="state">
      <label class="form-check-label ugcs-form-label" for="state">Select by State</label>
    </div>
    {$sselect}
  </div>
  <div class="col-md-3">
    <label for="just_firewx" class="form-label ugcs-form-label">Zone Type</label>
    {$fselect}
  </div>
  <div class="col-md-1 d-flex align-items-end">
    <button type="submit" class="btn btn-primary w-100">View UGCs</button>
  </div>
</form>

<div class="ugcs-table-container">
  <h3 class="h5 mb-3">UGCs listing {$title}</h3>
  <div id="ugcs-table"></div>
</div>
EOM;
$t->render('full.phtml');
