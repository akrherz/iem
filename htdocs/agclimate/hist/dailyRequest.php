<?php 
 /* Daily Data download for the ISUAG Network */ 
 include("../../../config/settings.inc.php");
 include("../../../include/forms.php");
 define("IEM_APPID", 12);
 include("../../../include/myview.php");
 include_once "boxinc.phtml";
 $t = new MyView();
 $t->title = "ISU AgClimate Legacy Daily Data Request";
 $t->thispage ="networks-agclimate";

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

<table width="100%">
<tr><td valign="top">

<h4 class="subtitle">Select station(s):</h4>
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

<h4 class="subtitle">Select data:</h4>
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
  <input type="checkbox" name="vars[]" value="c70"> <a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [mm]<br />

</td></tr></table>

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
<i>
When selecting the time interval, make sure you that choose <B> * valid * </B> dates.
</i>
<TABLE>
  <TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
  <TR><TH>Starting On:</TH>
  <td>{$ys}</td>
  <td>{$ms}</td>
  <td>{$ds}</td>
 </tr>
</TR>
<TR><TH>Ending On:</TH>
  <td>{$ys2}</td>
  <td>{$ms2}</td>
  <td>{$ds2}</td>
 		</TR>
</TABLE>

<h4 class="subtitle">Options:</h4>
<div style="margin-left: 20px;">
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
<br>How should the values be separated?: 
<select name="delim">
  <option value="comma">by commas
  <option value="tab">by tabs
</select>
<br />Text file format:
<select name="lf">
  <option value="dos">Windows/DOS
  <option value="unix">UNIX/MacOSX
</select>
</div>

<p><b><h4>Submit your request:</h4></b>
	<input type="submit" value="Get Data">
	<input type="reset">

<BR>
</form>
EOF;
$t->render('single.phtml');
?>
