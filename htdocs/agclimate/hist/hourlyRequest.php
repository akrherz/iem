<?php
/* Daily Data download for the ISUAG Network */
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/myview.php";
define("IEM_APPID", 13);
require_once "boxinc.phtml";

$t = new MyView();
$t->iem_resource = "ISUSM";
$t->title = "ISU AgClimate Legacy Hourly Data Request";

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
   <li class="breadcrumb-item active" aria-current="page">Legacy Network Hourly Download</li>
  </ol>
 </nav>
{$box}

<div class="card mb-4">
<div class="card-header">
<h4 class="mb-0">Hourly Data Request Form</h4>
</div>
<div class="card-body">

<p>This interface allows the download of hourly data from the legacy
ISU AgClimate Network sites.  Data for some of these sites exists back 
till 1986 until they all were removed in 2014.  In general, 
<strong>the precipitation data is of poor quality and should not be used.</strong>
If you are looking for daily 
data from this network, see <a href="dailyRequest.php">this page</a>.</p>

<form method="GET" action="worker.php">
<input type="hidden" name="startHour" value="0">

<div class="row">
<div class="col-md-6">

<div class="mb-4">
<h5>Select station(s):</h5>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A130209" id="ames">
    <label class="form-check-label" for="ames">Ames</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A131069" id="calmar">
    <label class="form-check-label" for="calmar">Calmar</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A131299" id="castana">
    <label class="form-check-label" for="castana">Castana</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A131329" id="cedar">
    <label class="form-check-label" for="cedar">Cedar Rapids</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A131559" id="chariton">
    <label class="form-check-label" for="chariton">Chariton</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A131909" id="crawford">
    <label class="form-check-label" for="crawford">Crawfordsville</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A130219" id="gilbert">
    <label class="form-check-label" for="gilbert">Gilbert</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A134309" id="kanawha">
    <label class="form-check-label" for="kanawha">Kanawha</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A134759" id="lewis">
    <label class="form-check-label" for="lewis">Lewis</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A135849" id="muscatine">
    <label class="form-check-label" for="muscatine">Muscatine</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A135879" id="nashua">
    <label class="form-check-label" for="nashua">Nashua</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A136949" id="rhodes">
    <label class="form-check-label" for="rhodes">Rhodes</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="sts[]" value="A138019" id="sutherland">
    <label class="form-check-label" for="sutherland">Sutherland</label>
</div>
</div>

</div>
<div class="col-md-6">

<div class="mb-4">
<h5>Select data:</h5>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c100" id="temp">
    <label class="form-check-label" for="temp">Air Temperature [F]</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c800" id="solar">
    <label class="form-check-label" for="solar">Solar Radiation Values [kilo calorie per meter squared per hour]</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c900" id="precip">
    <label class="form-check-label" for="precip">Precipitation [inches]</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c300" id="soil">
    <label class="form-check-label" for="soil">4 inch Soil Temperatures [F]</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c200" id="humidity">
    <label class="form-check-label" for="humidity">Relative Humidity [%]</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c400" id="wind_speed">
    <label class="form-check-label" for="wind_speed">Wind Speed [MPH] (~3 meter height)</label>
</div>
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="vars[]" value="c600" id="wind_dir">
    <label class="form-check-label" for="wind_dir">Wind Direction [deg] (~3 meter height)</label>
</div>
</div>

</div>
</div>

<div class="mb-4">
<h5>Select the time interval:</h5>
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
<input class="form-check-input" type="checkbox" name="qcflags" value="yes" id="qcflags">
<label class="form-check-label" for="qcflags">Include QC Flags</label>
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
<input class="form-check-input" type="checkbox" name="todisk" value="yes" id="todisk">
<label class="form-check-label" for="todisk">Download directly to disk</label>
</div>

<div class="row mb-3">
<div class="col-md-6">
<label for="delim" class="form-label">Delimination:</label>
<select name="delim" id="delim" class="form-select">
  <option value="comma">Comma Delimited</option>
  <option value="tab">Tab Delimited</option>
</select>
</div>
<div class="col-md-6">
<label for="lf" class="form-label">Text file format:</label>
<select name="lf" id="lf" class="form-select">
  <option value="dos">Windows/DOS</option>
  <option value="unix">UNIX/MacOSX</option>
</select>
</div>
</div>

</div>
</div>

<div class="mb-3">
<h5>Submit your request:</h5>
<div class="d-flex gap-2">
<input type="submit" value="Submit Query" class="btn btn-primary">
<input type="reset" value="Reset Form" class="btn btn-secondary">
</div>
</div>

</form>
</div>
</div>

EOM;
$t->render('single.phtml');
