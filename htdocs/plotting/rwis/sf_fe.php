<?php
$OL = "10.10.0";
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_RWIS";
$ostation = isset($_GET["ostation"]) ? xssafe($_GET["ostation"]) : "";
$station = isset($_GET['station']) ? xssafe($_GET["station"]) : "";
$syear = get_int404("syear", date("Y"));
$smonth = isset($_GET["smonth"]) ? xssafe($_GET["smonth"]) : date("m");
$sday = isset($_GET["sday"]) ? xssafe($_GET["sday"]) : date("d");
$days = get_int404("days", 2);

$subc = isset($_GET["subc"]) ? xssafe($_GET["subc"]) : false;
$dwpf = isset($_GET["dwpf"]) ? xssafe($_GET["dwpf"]) : false;
$tmpf = isset($_GET["tmpf"]) ? xssafe($_GET["tmpf"]) : false;
$pcpn = isset($_GET["pcpn"]) ? xssafe($_GET["pcpn"]) : false;
$s0 = isset($_GET["s0"]) ? xssafe($_GET["s0"]) : false;
$s1 = isset($_GET["s1"]) ? xssafe($_GET["s1"]) : false;
$s2 = isset($_GET["s2"]) ? xssafe($_GET["s2"]) : false;
$s3 = isset($_GET["s3"]) ? xssafe($_GET["s3"]) : false;

if (!$subc && !$dwpf && !$tmpf && !$s0 && !$s1 && !$s2 && !$s3) {
    $_GET["tmpf"] = "on";
}

$t = new MyView();
$t->iemselect2 = TRUE;
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="sf_fe.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.js"></script>
EOM;
$t->title = "RWIS Timeseries Plots";

$nselect = selectNetworkType("RWIS", $network);
$addSelectAttributes = fn($select, $id) => str_replace(
    "<select ",
    "<select id=\"{$id}\" ",
    str_replace('class="iemselect2"', 'class="form-select iemselect2"', $select),
);
$networkSelect = $addSelectAttributes($nselect, "network");

$content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb mb-3">
    <li class="breadcrumb-item"><a href="/RWIS/">RWIS Homepage</a></li>
    <li class="breadcrumb-item active" aria-current="page">RWIS Temperature Time Series Plots</li>
</ol>
</nav>

<header class="mb-4">
<h1 class="h3">RWIS Temperature Time Series Plots</h1>
<p class="mb-0">Plot a time series from an Iowa RWIS site, with optional sensors and archive dates.</p>
</header>

<form method="GET" action="sf_fe.php" name="sts" class="card shadow-sm mb-4">
<div class="card-body">
<div class="row g-3 align-items-end">
<div class="col-md-8">
<label for="network" class="form-label">RWIS network</label>
{$networkSelect}
</div>
<div class="col-md-4">
<button type="submit" class="btn btn-primary">Show network</button>
</div>
</div>
</div>
</form>

<form method="GET" action="sf_fe.php" name="olselect">
<input type="hidden" name="network" value="{$network}">
EOM;
if (strlen($station) > 0) {
    $ys = yearSelect(1995, $syear, "syear");
    $ms =  monthSelect($smonth, "smonth");
    $ds = daySelect($sday, "sday");
    $ds2 = daySelect($days, "days");
    $addFormSelectClass = fn($select) => str_replace(
        "<select ",
        '<select class="form-select" ',
        $select,
    );
    $ys = $addSelectAttributes($addFormSelectClass($ys), "syear");
    $ms = $addSelectAttributes($addFormSelectClass($ms), "smonth");
    $ds = $addSelectAttributes($addFormSelectClass($ds), "sday");
    $ds2 = $addSelectAttributes($addFormSelectClass($ds2), "days");
    $nselect = networkSelect($network, $station, array(), "station", FALSE, "form-select iemselect2");
    $nselect = $addSelectAttributes($nselect, "station");

    $c0 = iemdb('rwis');
    $stname = iem_pg_prepare($c0, "SELECT s.* from sensors s JOIN stations t on (s.iemid = t.iemid) WHERE t.id = $1");
    $r0 = pg_execute($c0, $stname, Array($station));
    $ns0 = "Sensor 1";
    $ns1 = "Sensor 2";
    $ns2 = "Sensor 3";
    $ns3 = "Sensor 4";
    if (pg_num_rows($r0) > 0){
        $row = pg_fetch_assoc($r0);
        $ns0 = $row['sensor0'];
        $ns1 = $row['sensor1'];
        $ns2 = $row['sensor2'];
        $ns3 = $row['sensor3'];
    }
    $cgiStr = "&sday=$sday&smonth=$smonth&syear=$syear&days=$days&";

    foreach (array("s0", "s1", "s2", "s3", "tmpf", "dwpf", "subc", "pcpn") as $name) {
        if (isset($_GET[$name])) {
            $cgiStr .= "&{$name}=yes";
        }
    }
    $addCheckbox = fn($name, $label) => sprintf(
        '<div class="form-check"><input class="form-check-input" type="checkbox" name="%s" id="%s" value="yes"%s><label class="form-check-label" for="%s">%s</label></div>',
        $name,
        $name,
        isset($_GET[$name]) ? " checked" : "",
        $name,
        $label,
    );
    $limitCheckbox = $addCheckbox("limit", "Temperatures between 25-35");
    $s0Checkbox = strlen($ns0) > 0 ? $addCheckbox("s0", $ns0) : "";
    $s1Checkbox = strlen($ns1) > 0 ? $addCheckbox("s1", $ns1) : "";
    $s2Checkbox = strlen($ns2) > 0 ? $addCheckbox("s2", $ns2) : "";
    $s3Checkbox = strlen($ns3) > 0 ? $addCheckbox("s3", $ns3) : "";
    $tmpfCheckbox = $addCheckbox("tmpf", "Air Temperature");
    $dwpfCheckbox = $addCheckbox("dwpf", "Dew Point");
    $subcCheckbox = $addCheckbox("subc", "Sub Surface");
    $pcpnCheckbox = $addCheckbox("pcpn", "Precipitation");
    $table = <<<EOM
<div class="row g-3">
<div class="col-md-4">
<fieldset>
<legend class="h6">Plot range</legend>
{$limitCheckbox}
</fieldset>
</div>
<div class="col-md-4">
<fieldset>
<legend class="h6">Pavement sensors</legend>
{$s0Checkbox}
{$s1Checkbox}
{$s2Checkbox}
{$s3Checkbox}
</fieldset>
</div>
<div class="col-md-4">
<fieldset>
<legend class="h6">Other sensors</legend>
{$tmpfCheckbox}
{$dwpfCheckbox}
{$subcCheckbox}
{$pcpnCheckbox}
</fieldset>
</div>
</div>
EOM;

    if (isset($_GET["limit"]))  $cgiStr .= "&limit=yes";
    $plots = "<p>No Soil/Traffic data for non-Iowa RWIS sites</p>";
    if ($network == "IA_RWIS"){
        $plots = <<<EOM
<br><img src="plot_traffic.php?station={$station}&network={$network}{$cgiStr}" alt="Time Series" class="img-fluid"/>
<br><img src="plot_soil.php?station={$station}&network={$network}{$cgiStr}" alt="Time Series" class="img-fluid"/>
EOM;
    }

    $content .= <<<EOM
<div class="row g-4 mb-4">
<div class="col-lg-5">
<section class="card h-100" aria-labelledby="station-heading">
<div class="card-header"><h2 id="station-heading" class="h5 mb-0">Station</h2></div>
<div class="card-body">
<label for="station" class="form-label">RWIS station</label>
{$nselect}
<div class="form-text">Or choose a station from the <a href="sf_fe.php">map</a>.</div>
</div>
</section>
</div>
<div class="col-lg-7">
<section class="card h-100" aria-labelledby="timespan-heading">
<div class="card-header"><h2 id="timespan-heading" class="h5 mb-0">Timespan</h2></div>
<div class="card-body">
<div class="row g-3">
<div class="col-sm-6 col-lg-3"><label for="syear" class="form-label">Start year</label>{$ys}</div>
<div class="col-sm-6 col-lg-3"><label for="smonth" class="form-label">Start month</label>{$ms}</div>
<div class="col-sm-6 col-lg-3"><label for="sday" class="form-label">Start day</label>{$ds}</div>
<div class="col-sm-6 col-lg-3"><label for="days" class="form-label">Number of days</label>{$ds2}</div>
</div>
</div>
</section>
</div>
</div>

<section class="card mb-4" aria-labelledby="options-heading">
<div class="card-header"><h2 id="options-heading" class="h5 mb-0">Plot options</h2></div>
<div class="card-body">
{$table}
</div>
</section>

<button type="submit" class="btn btn-primary mb-4">Generate plot</button>
</form>

<section aria-labelledby="plots-heading">
<h2 id="plots-heading" class="h5 mb-3">Generated plots</h2>
<div class="mb-4"><img src="SFtemps.php?station={$station}&network={$network}{$cgiStr}" alt="RWIS temperature time series" class="img-fluid"/></div>
{$plots}
</section>
EOM;
} else {
    $nselect = networkSelect($network, "");
        $nselect = $addSelectAttributes($nselect, "station");
    $content .= <<<EOM
<input type="hidden" name="s0" value="yes" />
<input type="hidden" name="s1" value="yes" />
<input type="hidden" name="s2" value="yes" />
<input type="hidden" name="s3" value="yes" />
<input type="hidden" name="tmpf" value="yes" />
<input type="hidden" name="dwpf" value="yes" />
<div class="row g-4 mb-4">
<div class="col-lg-5">
<section class="card" aria-labelledby="station-heading">
<div class="card-header"><h2 id="station-heading" class="h5 mb-0">Select station</h2></div>
<div class="card-body">
<label for="station" class="form-label">RWIS station</label>
{$nselect}
<button type="submit" class="btn btn-primary mt-3">Make plot</button>
</div>
</section>
</div>
<div class="col-lg-7">
<section class="card" aria-labelledby="map-heading">
<div class="card-header"><h2 id="map-heading" class="h5 mb-0">Select from map</h2></div>
<div class="card-body"><div id="map" data-network="{$network}" class="border rounded" style="min-height: 24rem;"></div></div>
</section>
</div>
</div>
</form>


  </form>

EOM;
}
$t->content = $content;
$t->render('single.phtml');
