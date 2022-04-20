<?php
// Pest DD Maps
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";

// defaults
$year = date("Y");
// yesterday
$day = date("Y-m-d", time() - 86400);

// Get things set via CGI
$pest = isset($_GET["pest"]) ? xssafe($_GET["pest"]) : null;
$sdate = isset($_GET["sdate"]) ? xssafe($_GET["sdate"]) : "$year-01-01";
$edate = isset($_GET["edate"]) ? xssafe($_GET["edate"]) : $day;
$edatechecked = isset($_GET["edate"]) ? "" : "checked";

$t = new MyView();
$t->title = "Pest Forecasting Maps";
$t->jsextra = <<<EOM
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script type="text/javascript" src="main.js"></script>
EOM;
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<style>
#theimage {
  display: block;
  background-image: url("/images/wait24trans.gif");
  background-position: center top;
  background-repeat: no-repeat;
  background-size: 80px 80px;
  min-height: 100px;
  min-width: 400px;
}
</style>
EOM;

// Compute a good fall Year
$year = intval(date("Y"));

$ar = Array(
    "seedcorn_maggot" => "Seedcorn Maggot (Delia platura)",
    "alfalfa_weevil" => "Alfalfa Weevil (Hypera postica)",
    "soybean_aphid" => "Soybean Aphid (Aphis glycines)",
    "common_stalk_borer" => "Common Stalk Borer (Papaipema nebris)",
    "japanese_beetle" => "Japanese Beetle (Popillia japonica)",
);
$pselect = make_select("pest", $pest, $ar, "updateImage", "form-control");

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/agweather/">Ag Weather</a></li>
 <li class="active">Pest Forecasting Maps</li>
 </ol>

<p>This page generates degree day maps for a selected pest. The pest provides
the base and ceiling values used in the degree day calculation. The IEM's
<a href="/climodat/">Climodat Stations</a> are used for the daily high and
low temperatures. <a href="/plotting/auto/?q=97">IEM Autoplot 97</a> is
the backend that generates the maps/data here.</p>

<form method="GET" name="main">

<div class="row">
<div class="col-md-6">
<label>Select Pest</label>
<br />${pselect}
</div>
<div class="col-md-3">
<label for="sdate">Start Date</label>
<input type="text" name="sdate" id="sdate" value="$sdate" class="form-control" placeholder="Start Date">
</div>
<div class="col-md-3">
<input type="checkbox" name="edate_off" id="edate_off" value="1" $edatechecked>
<label for="edate_off">Default to Latest End Date</label>
<input type="text" name="edate" id="edate" value="$edate" class="form-control" placeholder="Start Date">
</div>

</div><!-- end row -->

<div id="seedcorn_maggot" class="pinfo" style="display: none;">
<h3>Seedcorn Maggot (Delia platura)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>360:</strong> Peak adult emergence (1st generation) and egg-laying</li>
 <li><strong>781:</strong> Pupation, "fly-free" period begins</li>
 </ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/seedcorn-maggot">Extension Encyclopedia</a></p>
</div>

<div id="alfalfa_weevil" class="pinfo" style="display: none;">
<h3>Alfalfa Weevil (Hypera postica)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>300:</strong> Egg hatch</li>
 <li><strong>575:</strong> Peak larval feeding</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/alfalfa-weevil">Extension Encyclopedia</a></p>
</div>

<div id="soybean_aphid" class="pinfo" style="display: none;">
<h3>Soybean Aphid (Aphis glycines)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>150:</strong> Egg hatch</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/soybean-aphid">Extension Encyclopedia</a></p>
</div>

<div id="common_stalk_borer" class="pinfo" style="display: none;">
<h3>Common Stalk Borer (Papaipema nebris)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>1,400</strong>: Larvae begin moving to cornfields</li>
 <li><strong>1,700</strong>: Peak larval movement</li>
</ul>

<p>Extension Encyclopedia TBD</p>
</div>

<div id="japanese_beetle" class="pinfo" style="display: none;">
<h3>Japanese Beetle (Popillia japonica)</h3>
<p>Key Degree Day Levels:</p>
<ul>
 <li><strong>1,030</strong>: Adults begin emerging</li>
 <li><strong>2,150</strong>: Adults done emerging</li>
</ul>

<p><a href="https://crops.extension.iastate.edu/encyclopedia/japanese-beetle-corn-and-soybean">Extension Encyclopedia</a></p>
</div>


<div id="willload" style="height: 200px;">
<p><span class="fa fa-arrow-down"></span>
This application takes about 10 seconds to generate a map.
Hold on for the map is generating now!</p>
<div class="progress progress-striped active">
    <div id="timingbar" class="progress-bar progress-bar-warning" role="progressbar"
        aria-valuenow="0" aria-valuemin="0" aria-valuemax="10"
        style="width: 0%;"></div>
</div>
</div>
<br clear="all" />

<div class="row"><div class="col-md-12">
<img id="theimage" src="/images/pixel.gif" class="img img-responsive">
</div></div>

<div id="thedata"></div>

</form>


EOM;
$t->render("single.phtml");
