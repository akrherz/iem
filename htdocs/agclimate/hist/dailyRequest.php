<?php 
 /* Daily Data download for the ISUAG Network */ 
 include("../../../config/settings.inc.php");
 define("IEM_APPID", 12);
 $TITLE = "IEM | ISU Agclimate | Daily Data Request";
 $THISPAGE="networks-agclimate";
 include("$rootpath/include/header.php"); 
 include("$rootpath/include/forms.php");
?>
<h3 class="heading">Daily Data Request Form:</h3>
<div class="text">
<P><b>Information:</b> This interface accesses the archive of daily weather 
data collected from 
the Iowa State Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 

<P><B>Data Interval:</B>Currently you are selected to download daily data. 
You may wish to change this to <a href="hourlyRequest.php">hourly data</a>. 


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
  <input type="checkbox" name="vars[]" value="c40">Average Windspeed (MPH)<BR>
  <input type="checkbox" name="vars[]" value="c509">Max Wind Gust -- 1 min (MPH)<BR>
  <input type="checkbox" name="vars[]" value="c529">Max Wind Gust -- 5 sec (MPH)<BR>
  <input type="checkbox" name="vars[]" value="c90">Daily Precipitation (inch)<BR>
  <input type="checkbox" name="vars[]" value="c20">Average Relative Humidity (%)<BR>
  <input type="checkbox" name="vars[]" value="c80">Solar Radiation (langley)<BR>
  <input type="checkbox" name="vars[]" value="c70">Evapotranspiration (inch)<br />

</td></tr></table>

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
<i>
When selecting the time interval, make sure you that choose <B> * valid * </B> dates.
</i>
<TABLE>
  <TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
  <TR><TH>Starting On:</TH>
    <TD><?php echo yearSelect2(1986, date("Y"), "startYear"); ?></TD>
   <td><?php echo monthSelect(1, "startMonth"); ?></td>
 <td><?php echo daySelect2(1, "startDay"); ?></td>
 </tr>
</TR>
<TR><TH>Ending On:</TH>
 <TD><?php echo yearSelect2(1986, date("Y"), "endYear"); ?></TD>
 <td><?php echo monthSelect(date("m"), "endMonth"); ?></td>
 <td><?php echo daySelect2(date("d"), "endDay"); ?></td>
</TR>
</TABLE>

<h4 class="subtitle">Options:</h4>
<div style="margin-left: 20px;">
<input type="checkbox" name="qcflags" value="yes">Include quality control flags
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

<p><b><h4 class="subtitle">Submit your request:</h4></b>
	<input type="submit" value="Get Data">
	<input type="reset">

<BR>
</form></div>

<?php include("$rootpath/include/footer.php"); ?>
