<?php
// Frontend for the ISUSM Daily Data Download
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
require_once "boxinc.phtml";

$t = new MyView();
$t->iem_resource = "ISUSM";
$t->title = "ISU Soil Moisture Daily Data Request";

$nt = new NetworkTable("ISUSM");

$yselect = yearSelect(2013, date("Y"), "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect(1, "day1");
$yselect2 = yearSelect(2013, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect(date("d"), "day2");

$sselect = "";
foreach ($nt->table as $key => $val) {
    $sselect .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label class="form-check-label" for="%s">%s (%s County, %s)</label>' .
        '</div>',
        $key,
        $key,
        $key,
        $val["name"],
        $val["county"],
        $key
    );
}

$soilopts = "";
$levels = array(4, 12, 24, 50);
foreach ($levels as $key => $val) {
    $soilopts .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="vars" value="soil%02dtn" ' .
            'id="soil%02dtn"> <label class="form-check-label" for="soil%02dtn">' .
            'Daily Low %s inch Soil Temperature [F]</label>' .
        '</div>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
    $soilopts .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="vars" value="soil%02dt" ' .
            'id="soil%02dt"> <label class="form-check-label" for="soil%02dt">' .
            'Daily Average %s inch Soil Temperature [F]</label>' .
        '</div>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
    $soilopts .= sprintf(
        '<div class="form-check">' .
            '<input class="form-check-input" type="checkbox" name="vars" value="soil%02dtx" ' .
            'id="soil%02dtx"> <label class="form-check-label" for="soil%02dtx">' .
            'Daily High %s inch Soil Temperature [F]</label>' .
        '</div>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
}

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/agclimate">ISU Soil Moisture Network</a></li>
<li class="breadcrumb-item active" aria-current="page">Daily Download</li>
</ol>
</nav>

{$box}

<div class="card mb-4">
<div class="card-header">
<h3 class="mb-0">Daily Data Request Form</h3>
</div>
<div class="card-body">

<div class="alert alert-info mb-3">
<strong>Information:</strong> This interface accesses the archive of daily weather 
data collected from the Iowa State Agclimate Automated Weather stations. Please
select the stations and weather variables desired below.
</div>

<div class="alert alert-warning mb-3">
<strong>Data Interval:</strong> Currently you are selected to download daily data. 
You may wish to change this to <a href="hourly.php">hourly data</a>.
</div>

<p><a href="/cgi-bin/request/isusm.py?help" class="btn btn-info">
<i class="bi bi-file-earmark-text"></i> Backend documentation</a> exists for those
wishing to script against this data service.</p>

<form name="dl" method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="daily" />

<div class="row">
<div class="col-md-6">

<div class="mb-4">
<h5>Select station(s):</h5>
<p><a href="/sites/networks.php?network=ISUSM&format=html">View station metadata</a></p>
{$sselect}
</div>

<div class="mb-4">
<h5>Select the time interval:</h5>
<div class="alert alert-info">
<small><em>When selecting the time interval, make sure you choose <strong>valid</strong> dates.</em></small>
</div>
<div class="table-responsive">
<table class="table table-bordered">
<thead class="table-light">
<tr><th></th><th>Year:</th><th>Month:</th><th>Day:</th></tr>
</thead>
<tbody>
<tr><th>Starting On:</th>
<td>{$yselect}</td>
<td>{$mselect}</td>
<td>{$dselect}</td>
</tr>
<tr><th>Ending On:</th>
<td>{$yselect2}</td>
<td>{$mselect2}</td>
<td>{$dselect2}</td>
</tr>
</tbody>
</table>
</div>
</div>

<div class="card mb-4">
<div class="card-header">
<h5 class="mb-0">Variables</h5>
</div>
<div class="card-body">

<div class="mb-3">
<strong>Select from available variables</strong>
</div>

<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="high" id="high">
<label class="form-check-label" for="high">High Temperature [F]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="low" id="low">
<label class="form-check-label" for="low">Low Temperature [F]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="chillhours" id="chillhours">
<label class="form-check-label" for="chillhours">Daily Chill Hours,</label>
<div class="d-inline-flex gap-2 ms-2">
<span>Base (&deg;F):</span> <input type="text" size="3" value="32" name="chillbase" class="form-control form-control-sm">
<span>Ceiling (&deg;F):</span> <input type="text" size="3" value="45" name="chillceil" class="form-control form-control-sm">
</div>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="rh_min" id="rh_min">
<label class="form-check-label" for="rh_min">Minimum Relative Humidity [%]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="rh" id="rh">
<label class="form-check-label" for="rh">Average Relative Humidity [%]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="rh_max" id="rh_max">
<label class="form-check-label" for="rh_max">Maximum Relative Humidity [%]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="gdd50" id="gdd50">
<label class="form-check-label" for="gdd50">Growing Degree Days (base 50) [F]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="solar" id="solar">
<label class="form-check-label" for="solar">Solar Radiation [J/m^2]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="solar_mj" id="solar_mj">
<label class="form-check-label" for="solar_mj">Solar Radiation [MJ/m^2]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="precip" id="precip">
<label class="form-check-label" for="precip">Precipitation [inch]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="speed" id="speed">
<label class="form-check-label" for="speed">Average Wind Speed [mph]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="gust" id="gust">
<label class="form-check-label" for="gust">Wind Gust [mph]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="et" id="et">
<label class="form-check-label" for="et">Reference Evapotranspiration [inch] <a href="/agclimate/et.phtml" target="_new">More Info</a></label>
</div>

{$soilopts}

<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="soil12vwc" id="soil12vwc">
<label class="form-check-label" for="soil12vwc">12 inch Soil Moisture [%]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="soil24vwc" id="soil24vwc">
<label class="form-check-label" for="soil24vwc">24 inch Soil Moisture [%]</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="soil50vwc" id="soil50vwc">
<label class="form-check-label" for="soil50vwc">50 inch Soil Moisture [%]</label>
</div>

<hr>

<div class="mb-3">
<strong>Vineyard Station-only Variables</strong>
<small class="d-block text-muted">Sorry for the cryptic labels, this is a current work in progress.</small>
</div>

<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmv_1" id="lwmv_1">
<label class="form-check-label" for="lwmv_1">lwmv_1</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmv_2" id="lwmv_2">
<label class="form-check-label" for="lwmv_2">lwmv_2</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmdry_1_tot" id="lwmdry_1_tot">
<label class="form-check-label" for="lwmdry_1_tot">lwmdry_1_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmcon_1_tot" id="lwmcon_1_tot">
<label class="form-check-label" for="lwmcon_1_tot">lwmcon_1_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmwet_1_tot" id="lwmwet_1_tot">
<label class="form-check-label" for="lwmwet_1_tot">lwmwet_1_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmdry_2_tot" id="lwmdry_2_tot">
<label class="form-check-label" for="lwmdry_2_tot">lwmdry_2_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmcon_2_tot" id="lwmcon_2_tot">
<label class="form-check-label" for="lwmcon_2_tot">lwmcon_2_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="lwmwet_2_tot" id="lwmwet_2_tot">
<label class="form-check-label" for="lwmwet_2_tot">lwmwet_2_tot</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="bpres_avg" id="bpres_avg">
<label class="form-check-label" for="bpres_avg">bpres_avg</label>
</div>

<hr>

<div class="mb-3">
<p>The Ames-AEA, Ames-Kitchen, and Jefferson locations have the
<a href="https://www.campbellsci.com/soilvue10">CS SoilVue 10</a> installed.</p>

<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars" value="sv" id="sv">
<label class="form-check-label" for="sv">SoilVue Temperature + Moisture Data</label>
</div>
</div>

</div>
</div>

<div class="card mb-4">
<div class="card-header">
<h5 class="mb-0">Options</h5>
</div>
<div class="card-body">

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="todisk" value="yes" id="todisk">
<label class="form-check-label" for="todisk">Download directly to disk</label>
</div>

<div class="mb-3">
<label for="format" class="form-label"><strong>How should the data be formatted?:</strong></label>
<select name="format" id="format" class="form-select">
<option value="excel">Microsoft Excel (xlsx)</option>
<option value="comma">Comma Delimited Text File</option>
<option value="tab">Tab Delimited Text File</option>
</select>
</div>

<div class="mb-3">
<label for="missing" class="form-label"><strong>How should missing values be represented?:</strong></label>
<select name="missing" id="missing" class="form-select">
<option value="-99">-99</option>
<option value="M">M</option>
<option value="">(blank, empty space)</option>
</select>
</div>

{$qcbox}

<div class="mb-3">
<h6><strong>Submit your request:</strong></h6>
<div class="d-flex gap-2">
<input type="submit" value="Get Data" class="btn btn-primary">
<input type="reset" value="Reset Form" class="btn btn-secondary">
</div>
</div>

</div>
</div>

</form>

</div>
<div class="col-md-6">

<div class="card">
<div class="card-header">
<h4 class="mb-0">Meaning of Data Columns</h4>
</div>
<div class="card-body">

<dl class="row">
<dt class="col-sm-4">station</dt>
<dd class="col-sm-8">National Weather Service Location Identifier for the
site. This is a five character identifier.</dd>

<dt class="col-sm-4">valid</dt>
<dd class="col-sm-8">Date of the observation</dd>

<dt class="col-sm-4">high</dt>
<dd class="col-sm-8">High Temperature [F]</dd>
<dt class="col-sm-4">low</dt>
<dd class="col-sm-8">Low Temperature [F]</dd>
<dt class="col-sm-4">rh</dt>
<dd class="col-sm-8">Average Relative Humidity [%]</dd>
<dt class="col-sm-4">rh_max</dt>
<dd class="col-sm-8">Maximum Relative Humidity based on hourly observations [%]</dd>
<dt class="col-sm-4">rh_min</dt>
<dd class="col-sm-8">Minimum Relative Humidity based on hourly observations [%]</dd>
<dt class="col-sm-4">gdd50</dt>
<dd class="col-sm-8">Growing Degree Days [F]</dd>
<dt class="col-sm-4">solar</dt>
<dd class="col-sm-8">Solar Radiation [J/m^2]</dd>
<dt class="col-sm-4">precip</dt>
<dd class="col-sm-8">Precipitation [inch]</dd>
<dt class="col-sm-4">speed</dt>
<dd class="col-sm-8">Average Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
<dt class="col-sm-4">gust</dt>
<dd class="col-sm-8">Peak Wind Gust [mph], 10 minute average, 10 ft above ground</dd>
<dt class="col-sm-4">et</dt>
<dd class="col-sm-8">Evapotranspiration [inch]</dd>
<dt class="col-sm-4">soil04tn</dt>
<dd class="col-sm-8">Daily Low 4 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil04t</dt>
<dd class="col-sm-8">Daily Average 4 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil04tx</dt>
<dd class="col-sm-8">Daily High 4 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil12tn</dt>
<dd class="col-sm-8">Daily Low 12 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil12t</dt>
<dd class="col-sm-8">Daily Average 12 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil12tx</dt>
<dd class="col-sm-8">Daily High 12 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil24tn</dt>
<dd class="col-sm-8">Daily Low 24 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil24t</dt>
<dd class="col-sm-8">Daily Average 24 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil24tx</dt>
<dd class="col-sm-8">Daily High 24 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil50tn</dt>
<dd class="col-sm-8">Daily Low 50 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil50t</dt>
<dd class="col-sm-8">Daily Average 50 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil50tx</dt>
<dd class="col-sm-8">Daily High 50 inch Depth Soil Temperature [F]</dd>
<dt class="col-sm-4">soil12vwc</dt>
<dd class="col-sm-8">Average 12 inch Depth Soil Volumetric Water Content [%]</dd>
<dt class="col-sm-4">soil24vwc</dt>
<dd class="col-sm-8">Average 24 inch Depth Soil Volumetric Water Content [%]</dd>
<dt class="col-sm-4">soil50vwc</dt>
<dd class="col-sm-8">Average 50 inch Depth Soil Volumetric Water Content [%]</dd>
</dl>

</div>
</div>

</div>
</div>

</div>
</div>

EOM;
$t->render("single.phtml");
