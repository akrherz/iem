<?php
/* Daily Data download for the ISUAG Network */
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
define("IEM_APPID", 13);
require_once "boxinc.phtml";
require_once "../../../include/myview.php";
$t = new MyView();
$t->title = "ISU AgClimate Legacy Hourly Data Request";

$ys = yearSelect2(1986, date("Y"), "startYear", '', 2014);
$ms = monthSelect(1, "startMonth");
$ds = daySelect2(1, "startDay");
$ys2 = yearSelect2(1986, date("Y"), "endYear", '', 2014);
$ms2 = monthSelect(date("m"), "endMonth");
$ds2 = daySelect2(date("d"), "endDay");

$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU AgClimate</a></li>
  <li class="active">Legacy Network Hourly Download</li>
 </ol>
{$box}

<h4>Hourly Data Request Form</h4>

<p>This interface allows the download of hourly data from the legacy
ISU AgClimate Network sites.  Data for some of these sites exists back 
till 1986 until they all were removed in 2014.  In general, 
<strong>the precipitation data is of poor quality and should not be used.</strong>
If you are looking for daily 
data from this network, see <a href="dailyRequest.php">this page</a>.

<form method="GET" action="worker.php">
<input type="hidden" name="startHour" value="0">

<table width="100%">
<tr><td valign="top">

<p><b><h4 class="subtitle">Select station(s):</h4></b>
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

</td><td valign="top">

<p><b><h4 class="subtitle">Select data:</h4></b>
  <input type="checkbox" name="vars[]" value="c100">Air Temperature [F]<BR>
  <input type="checkbox" name="vars[]" value="c800">Solar Radiation Values [kilo calorie per meter squared per hour]<br />
  <input type="checkbox" name="vars[]" value="c900">Precipitation [inches]<BR>
  <input type="checkbox" name="vars[]" value="c300">4 inch Soil Temperatures [F]<BR>
  <input type="checkbox" name="vars[]" value="c200">Relative Humidity [%]<BR>
  <input type="checkbox" name="vars[]" value="c400">Wind Speed [MPH] (~3 meter height)<BR>
  <input type="checkbox" name="vars[]" value="c600">Wind Direction [deg] (~3 meter height)<BR>
  <!-- no idea on units ATM
    <input type="checkbox" name="vars[]" value="c700"><a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [in/dy]<br />
    -->
</td></tr></table>

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
        <TABLE>
                <TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
                <TR><TH>Starting On:</TH>
                <td>${ys}</td>
                <td>${ms}</td>
                <td>${ds}</td>
                </TR>
                <TR><TH>Ending On:</TH>
                <td>${ys2}</td>
                <td>${ms2}</td>
                <td>${ds2}</td>
                </TR>
            </TABLE>

<p><b><h4 class="subtitle">Options:</h4></b>
<input type="checkbox" name="qcflags" value="yes">Include QC Flags
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
<br>Delimination: <select name="delim">
  <option value="comma">Comma Delimited
  <option value="tab">Tab Delimited
</select>

<br />Text file format:
<select name="lf">
  <option value="dos">Windows/DOS
  <option value="unix">UNIX/MacOSX
</select>


<p><b><h4 class="subtitle">Submit your request:</h4></b>
    <input type="submit" value="Submit Query">
    <input type="reset">

<BR><BR>
</form>
EOF;
$t->render('single.phtml');
