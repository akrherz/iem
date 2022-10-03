<?php
/* Daily Data download for the ISUAG Network */
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
define("IEM_APPID", 12);
require_once "../../../include/myview.php";
include_once "boxinc.phtml";
$t = new MyView();
$t->title = "ISU AgClimate Legacy Daily Data Request";

$ys = yearSelect2(1986, date("Y"), "startYear", '', 2014);
$ms = monthSelect(1, "startMonth");
$ds = daySelect2(1, "startDay");
$ys2 = yearSelect2(1986, date("Y"), "endYear", '', 2014);
$ms2 = monthSelect(date("m"), "endMonth");
$ds2 = daySelect2(date("d"), "endDay");

$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU AgClimate</a></li>
  <li class="active">Legacy Network Daily Download</li>
 </ol>

{$box}

<h4>Daily Data Request Form</h4>

<p>This interface allows the download of daily summary data from the legacy
ISU AgClimate Network sites.  Data for some of these sites exists back 
till 1986 until they all were removed in 2014.  In general, 
<strong>the precipitation data is of poor quality and should not be used.</strong>
Please see the 
<a href="/request/coop/fe.phtml">NWS COOP download page</a> 
for high quality daily precipitation data.  If you are looking for hourly 
data from this network, see <a href="hourlyRequest.php">this page</a>.

<form name="dl" method="GET" action="worker.php">
<input type="hidden" name="timeType" value="daily">

<div class="row">
 <div class="col-md-6">

<h4>Select station(s):</h4>
  <input type="checkbox" name="sts[]" value="A130209">Ames<BR>
  <input type="checkbox" name="sts[]" value="A131069">Calmar<BR>
  <input type="checkbox" name="sts[]" value="A131299">Castana<BR>
  <input type="checkbox" name="sts[]" value="A131329">Cedar Rapids<BR>
  <input type="checkbox" name="sts[]" value="A131559">Chariton<BR>	
  <input type="checkbox" name="sts[]" value="A131909">Crawfordsville<BR>
  <input type="checkbox" name="sts[]" value="A130219">Gilbert<BR>
  <input type="checkbox" name="sts[]" value="A134309">Kanawha<BR>
  <input type="checkbox" name="sts[]" value="A134759">Lewis<BR>
  <input type="checkbox" name="sts[]" value="A135849">Muscatine<BR>
  <input type="checkbox" name="sts[]" value="A135879">Nashua<BR>
  <input type="checkbox" name="sts[]" value="A136949">Rhodes<BR>
  <input type="checkbox" name="sts[]" value="A138019">Sutherland<BR>

<h4>Select data:</h4>
  <input type="checkbox" name="vars[]" value="c11">High Temperature (F)<BR>
  <input type="checkbox" name="vars[]" value="c12">Low Temperature (F)<BR>
  <input type="checkbox" name="vars[]" value="c30l">Daily Low 4in Soil Temperature (F)<br />
  <input type="checkbox" name="vars[]" value="c30">Average 4in Soil Temperature (F)<BR>
  <input type="checkbox" name="vars[]" value="c30h">Daily Max 4in Soil Temperature (F)<br />
  <input type="checkbox" name="vars[]" value="c40">Average Windspeed (MPH) (~3 meter height)<BR>
  <input type="checkbox" name="vars[]" value="c509">Max Wind Gust -- 1 min (MPH)<BR>
  <input type="checkbox" name="vars[]" value="c529">Max Wind Gust -- 5 sec (MPH)<BR>
  <input type="checkbox" name="vars[]" value="c90">Daily Precipitation (inch)<BR>
  <input type="checkbox" name="vars[]" value="c20">Average Relative Humidity (%)<BR>
  <input type="checkbox" name="vars[]" value="c80">Solar Radiation (langley)<BR>
  <input type="checkbox" name="vars[]" value="c70"> <a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [inch]<br />

</div>
<div class="col-md-6">

<h4>Select the time interval:</h4>

<i>
When selecting the time interval, make sure you that choose <B> * valid * </B> dates.
</i>
<table>
<thead>
  <tr><th></th><th>Year:</th><th>Month:</th><th>Day:</th></tr>
</thead>

  <tr><th>Starting On:</th>
  <td>{$ys}</td>
  <td>{$ms}</td>
  <td>{$ds}</td>
 </tr>
</tr>
<tr><th>Ending On:</th>
  <td>{$ys2}</td>
  <td>{$ms2}</td>
  <td>{$ds2}</td>
         </tr>
</table>

<h4>Options:</h4>
<input type="checkbox" name="qcflags" value="yes">Include quality control flags
<table class="table table-striped">
<thead><tr><th>Flag</th><th>Meaning</th></tr></thead>
<tr>
  <th>M</th>
  <td>the data is missing</td></tr>

<tr>
  <th>E</th>
  <td>An instrument may be flagged until repaired</td></tr>

<tr>
  <th>R</th>
  <td>Estimate based on weighted linear regression from surrounding stations</td></tr>

<tr>
  <th>e</th>
  <td>We are not confident of the estimate</td></tr>

</table>
<br><input type="checkbox" name="todisk" value="yes">Download directly to disk

<p>How should the values be separated?: 
<select name="delim">
  <option value="comma">by commas
  <option value="tab">by tabs
</select>

<p>Text file format:
<select name="lf">
  <option value="dos">Windows/DOS</option>
  <option value="unix">UNIX/MacOSX</option>
</select>

<div class="alert alert-success"><strong>Pro-Tip</strong>: The downloaded text
files should be easily loaded into spreadsheet programs, like Microsoft Excel.
From Microsoft Excel, to go File-&gt;Open and set the file type to "All Files"
or something appropriate for delimited text.</div>

</div></div>

<p><b><h4>Submit your request:</h4></b>
    <input type="submit" value="Get Data">
    <input type="reset">

</form>

<br />
EOF;
$t->render('single.phtml');
