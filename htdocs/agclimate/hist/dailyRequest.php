<?php
/* Daily Data download for the ISUAG Network */
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
define("IEM_APPID", 12);
require_once "../../../include/myview.php";
require_once "../../../include/agclimate_boxinc.phtml";

$t = new MyView();
$t->iem_resource = "ISUSM";
$t->title = "ISU AgClimate Legacy Daily Data Request";

$ys = yearSelect(1986, date("Y"), "startYear", '', 2014);
$ms = monthSelect(1, "startMonth");
$ds = daySelect(1, "startDay");
$ys2 = yearSelect(1986, date("Y"), "endYear", '', 2014);
$ms2 = monthSelect(date("m"), "endMonth");
$ds2 = daySelect(date("d"), "endDay");

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/agclimate">ISU AgClimate</a></li>
<li class="breadcrumb-item active" aria-current="page">Legacy Network Daily Download</li>
</ol>
</nav>

{$box}

<div class="card mb-4">
<div class="card-header">
<h4 class="mb-0">Daily Data Request Form</h4>
</div>
<div class="card-body">

<p>This interface allows the download of daily summary data from the legacy
ISU AgClimate Network sites.  Data for some of these sites exists back 
till 1986 until they all were removed in 2014.  In general, 
<strong>the precipitation data is of poor quality and should not be used.</strong>
Please see the 
<a href="/request/coop/fe.phtml">NWS COOP download page</a> 
for high quality daily precipitation data.  If you are looking for hourly 
data from this network, see <a href="hourlyRequest.php">this page</a>.</p>

<form name="dl" method="GET" action="worker.php">
<input type="hidden" name="timeType" value="daily">

<div class="row">
<div class="col-md-6">

<div class="mb-4">
<h5>Select station(s):</h5>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A130209" id="ames_daily">
<label class="form-check-label" for="ames_daily">Ames</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A131069" id="calmar_daily">
<label class="form-check-label" for="calmar_daily">Calmar</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A131299" id="castana_daily">
<label class="form-check-label" for="castana_daily">Castana</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A131329" id="cedar_daily">
<label class="form-check-label" for="cedar_daily">Cedar Rapids</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A131559" id="chariton_daily">
<label class="form-check-label" for="chariton_daily">Chariton</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A131909" id="crawford_daily">
<label class="form-check-label" for="crawford_daily">Crawfordsville</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A130219" id="gilbert_daily">
<label class="form-check-label" for="gilbert_daily">Gilbert</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A134309" id="kanawha_daily">
<label class="form-check-label" for="kanawha_daily">Kanawha</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A134759" id="lewis_daily">
<label class="form-check-label" for="lewis_daily">Lewis</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A135849" id="muscatine_daily">
<label class="form-check-label" for="muscatine_daily">Muscatine</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A135879" id="nashua_daily">
<label class="form-check-label" for="nashua_daily">Nashua</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A136949" id="rhodes_daily">
<label class="form-check-label" for="rhodes_daily">Rhodes</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="sts[]" value="A138019" id="sutherland_daily">
<label class="form-check-label" for="sutherland_daily">Sutherland</label>
</div>
</div>

<div class="mb-4">
<h5>Select data:</h5>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c11" id="high_temp">
<label class="form-check-label" for="high_temp">High Temperature (F)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c12" id="low_temp">
<label class="form-check-label" for="low_temp">Low Temperature (F)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c30l" id="soil_low">
<label class="form-check-label" for="soil_low">Daily Low 4in Soil Temperature (F)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c30" id="soil_avg">
<label class="form-check-label" for="soil_avg">Average 4in Soil Temperature (F)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c30h" id="soil_high">
<label class="form-check-label" for="soil_high">Daily Max 4in Soil Temperature (F)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c40" id="wind_avg">
<label class="form-check-label" for="wind_avg">Average Windspeed (MPH) (~3 meter height)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c509" id="wind_gust_1">
<label class="form-check-label" for="wind_gust_1">Max Wind Gust -- 1 min (MPH)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c529" id="wind_gust_5">
<label class="form-check-label" for="wind_gust_5">Max Wind Gust -- 5 sec (MPH)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c90" id="precip_daily">
<label class="form-check-label" for="precip_daily">Daily Precipitation (inch)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c20" id="humidity_avg">
<label class="form-check-label" for="humidity_avg">Average Relative Humidity (%)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c80" id="solar_rad">
<label class="form-check-label" for="solar_rad">Solar Radiation (langley)</label>
</div>
<div class="form-check">
<input class="form-check-input" type="checkbox" name="vars[]" value="c70" id="evapo">
<label class="form-check-label" for="evapo"><a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [inch]</label>
</div>
</div>

</div>
<div class="col-md-6">

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
<td>{$ys}</td>
<td>{$ms}</td>
<td>{$ds}</td>
</tr>
<tr><th>Ending On:</th>
<td>{$ys2}</td>
<td>{$ms2}</td>
<td>{$ds2}</td>
</tr>
</tbody>
</table>
</div>
</div>

<div class="card mb-4">
<div class="card-header">
<h5 class="mb-0">Options</h5>
</div>
<div class="card-body">

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="qcflags" value="yes" id="qcflags_daily">
<label class="form-check-label" for="qcflags_daily">Include quality control flags</label>
</div>

<div class="table-responsive mb-3">
<table class="table table-striped">
<thead class="table-dark">
<tr><th>Flag</th><th>Meaning</th></tr>
</thead>
<tbody>
<tr>
<th>M</th>
<td>the data is missing</td>
</tr>
<tr>
<th>E</th>
<td>An instrument may be flagged until repaired</td>
</tr>
<tr>
<th>R</th>
<td>Estimate based on weighted linear regression from surrounding stations</td>
</tr>
<tr>
<th>e</th>
<td>We are not confident of the estimate</td>
</tr>
</tbody>
</table>
</div>

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="todisk" value="yes" id="todisk_daily">
<label class="form-check-label" for="todisk_daily">Download directly to disk</label>
</div>

<div class="row mb-3">
<div class="col-md-6">
<label for="delim_daily" class="form-label">How should the values be separated?:</label>
<select name="delim" id="delim_daily" class="form-select">
<option value="comma">by commas</option>
<option value="tab">by tabs</option>
</select>
</div>
<div class="col-md-6">
<label for="lf_daily" class="form-label">Text file format:</label>
<select name="lf" id="lf_daily" class="form-select">
<option value="dos">Windows/DOS</option>
<option value="unix">UNIX/MacOSX</option>
</select>
</div>
</div>

<div class="alert alert-success">
<strong>Pro-Tip</strong>: The downloaded text files should be easily loaded into spreadsheet programs, like Microsoft Excel.
From Microsoft Excel, go to File → Open and set the file type to "All Files" or something appropriate for delimited text.
</div>

</div>
</div>

</div>
</div>

<div class="mb-3">
<h5>Submit your request:</h5>
<div class="d-flex gap-2">
<input type="submit" value="Get Data" class="btn btn-primary">
<input type="reset" value="Reset Form" class="btn btn-secondary">
</div>
</div>

</form>
</div>
</div>


<br />

EOM;
$t->render('single.phtml');
