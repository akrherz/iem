<?php
// TODO print out dates that key thresholds are met
// TODO add climatology to the table
define("IEM_APPID", 135);

// Pest DD Maps
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";

// defaults
$year = date("Y");
// yesterday
$day = date("Y-m-d", time() - 86400);

// Get things set via CGI
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IACLIMATE";
$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : "IATAME";
$pest = isset($_GET["pest"]) ? xssafe($_GET["pest"]) : "seedcorn_maggot";
$sdate = isset($_GET["sdate"]) ? xssafe($_GET["sdate"]) : "$year-01-01";
$edate = isset($_GET["edate"]) ? xssafe($_GET["edate"]) : $day;
$edatechecked = isset($_GET["edate"]) ? "" : "checked";

// Folks may have this page bookmarked and thus get a wonky combination of
// start date and end date, rectify this
if ((! isset($_GET["edate"])) && isset($_GET["sdate"])) {
    $sdate = sprintf("%s-%s", $year, substr($sdate, 5, 5));
}

$sselect = selectNetworkType("CLIMATE", $network);

$t = new MyView();
$t->title = "Pest Forecasting Maps";
$t->jsextra = <<<EOM
<script type="module" src="index.module.js"></script>
EOM;
$t->headextra = <<<EOM
<link rel="stylesheet" href="index.css" />
EOM;

// Compute a good fall Year
$year = intval(date("Y"));

$ar = array(
    "seedcorn_maggot" => "Seedcorn Maggot (Delia platura)",
    "alfalfa_weevil" => "Alfalfa Weevil (Hypera postica)",
    "soybean_aphid" => "Soybean Aphid (Aphis glycines)",
    "common_stalk_borer" => "Common Stalk Borer (Papaipema nebris)",
    "japanese_beetle" => "Japanese Beetle (Popillia japonica)",
    "western_bean_cutworm" => "Western Bean Cutworm (Striacosta albicosta)",
    "european_corn_borer" => "European Corn Borer (Ostrinia nubilalis)",
);
$pselect = make_select("pest", $pest, $ar, "updatePest", "form-control");
$nselect = networkSelect($network, $station, array(), "station", TRUE);

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/agweather/">Ag Weather</a></li>
 <li class="breadcrumb-item active" aria-current="page">Pest Forecasting Maps</li>
 </ol>
</nav>

<p>This page generates degree day maps for a selected pest. The pest provides
the base and ceiling values used in the degree day calculation. The IEM's
<a href="/climodat/">Climodat Stations</a> are used for the daily high and
low temperatures. <a href="/plotting/auto/?q=97">IEM Autoplot 97</a> is
the backend that generates the maps/data here.</p>

<form method="GET" name="sswitch">
<p>$sselect <input type="submit" value="Switch State"></p>
</form>

<form method="GET" name="main">

<div class="row">
<div class="col-md-6">
<label>Select Pest</label>
<br />{$pselect}
</div>
<div class="col-md-3">
<label for="sdate">Start Date for Selected Pest</label>
<input type="text" name="sdate" id="sdate" value="$sdate" class="form-control">
</div>
<div class="col-md-3">
<input type="checkbox" name="edate_off" id="edate_off" value="1" $edatechecked>
<label for="edate_off">Default to Latest End Date</label>
<input type="text" name="edate" id="edate" value="$edate" class="form-control" placeholder="End Date">
</div>

</div><!-- end row -->

<div id="seedcorn_maggot" class="pinfo" style="display: none;">
<h3>Seedcorn Maggot (Delia platura)</h3>
<p>Key Degree Day Levels</p>
<ul>
 <li><strong>January 1:</strong> Start Date</li>
 <li><strong>360:</strong> Peak adult emergence (1st generation) and egg-laying</li>
 <li><strong>781:</strong> Pupation, "fly-free" period begins</li>
 </ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/seedcorn-maggot">Learn more here!</a></p>
</div>

<div id="alfalfa_weevil" class="pinfo" style="display: none;">
<h3>Alfalfa Weevil (Hypera postica)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>January 1:</strong> Start Date</li>
 <li><strong>300:</strong> Egg hatch</li>
 <li><strong>575:</strong> Peak larval feeding</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/alfalfa-weevil">Learn more here!</a></p>
</div>

<div id="soybean_aphid" class="pinfo" style="display: none;">
<h3>Soybean Aphid (Aphis glycines)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>January 1:</strong> Start Date</li>
 <li><strong>150:</strong> Egg hatch</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/soybean-aphid">Learn more here!</a></p>
</div>

<div id="common_stalk_borer" class="pinfo" style="display: none;">
<h3>Common Stalk Borer (Papaipema nebris)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>January 1:</strong> Start Date</li>
 <li><strong>1,400</strong>: Larvae begin moving to cornfields</li>
 <li><strong>1,700</strong>: Peak larval movement</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/stalk-borer">Learn more here!</a></p>
</div>

<div id="japanese_beetle" class="pinfo" style="display: none;">
<h3>Japanese Beetle (Popillia japonica)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>January 1:</strong> Start Date</li>
 <li><strong>1,030</strong>: Adults begin emerging</li>
 <li><strong>2,150</strong>: Adults done emerging</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/japanese-beetle-corn-and-soybean">Learn more here!</a></p>
</div>

<div id="western_bean_cutworm" class="pinfo" style="display: none;">
<h3>Western Bean Cutworm (Striacosta albicosta)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>March 1:</strong> Start Date</li>
 <li><strong>2,577</strong>: 25% moth flight</li>
</ul>

<p><a href="https://cropwatch.unl.edu/2021/degree-days-prediction-western-bean-cutworm-flight">Learn more here!</a></p>
</div>

<div id="european_corn_borer" class="pinfo" style="display: none;">
<h3>European Corn Borer (Ostrinia nubilalis)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>May 20:</strong> Approximate Start Date (actual start date is first spring moth capture)</li>
 <li><strong>212</strong>: 1st generation egg hatch</li>
 <li><strong>1,192</strong>: Egg-laying occurs</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/european-corn-borer">Learn more here!</a></p>
<p></p>
</div>


<div id="willload" style="height: 200px;">
<p><span class="fa fa-arrow-down"></span>
This application takes about 10 seconds to generate a map.
Hold on for the map is generating now!</p>
<div class="progress">
    <div id="timingbar" class="progress-bar bg-warning progress-bar-striped progress-bar-animated" role="progressbar"
        aria-valuenow="0" aria-valuemin="0" aria-valuemax="10"
        style="width: 0%;"></div>
</div>
</div>
<br clear="all" />

<div class="row">
<div class="col-md-9">
<img id="theimage" src="/images/pixel.gif" class="img-fluid">
<div id="thedata"></div>
</div>

<div class="col-md-3">
<strong>Point Data &amp; Forecast</strong>

<p>Select from the available stations for the observed data and a point
forecast based on the <a href="https://digital.weather.gov/">NWS NDFD</a>
and <a href="https://mag.ncep.noaa.gov/">NWS GFS Model</a>.</p>

<label>Select Station</label>
<br />{$nselect}

<table class="table table-striped">
<tbody>
<tr><th colspan="2">Observed <span id="station_date"></span></th></tr>
<tr><th>DD Accum:</th><td><span id="station_accum"></span></td></tr>

<tr><th colspan="2">NWS NDFD 7 Day Forecast
<br /><span id="station_ndfd_date"></span></th></tr>
<tr><th>DD Accum:</th><td><span id="station_ndfd_accum"></span></td></tr>
<tr><th>DD Total:</th><td><span id="station_ndfd_total"></span></td></tr>

<tr><th colspan="2">NWS GFS 14 Day Forecast
<br /><span id="station_gfs_date"></span></th></tr>
<tr><th>DD Accum:</th><td><span id="station_gfs_accum"></span></td></tr>
<tr><th>DD Total:</th><td><span id="station_gfs_total"></span></td></tr>

</tbody>
</table>
</div>
</div>

</form>


EOM;
$t->render("full.phtml");
