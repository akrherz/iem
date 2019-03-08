<?php 
 /* 
  * Download front end for daily data from the ISUSM network
  */
 include("../../../config/settings.inc.php");
 include("../../../include/myview.php");
 include("../../../include/network.php");
 include("../../../include/forms.php");
 include_once "boxinc.phtml";
 
 $t = new MyView();
 $t->title = "ISU Soil Moisture Daily Data Request";
 $t->thispage = "networks-agclimate";
 
 $nt = new NetworkTable("ISUSM");
 
 $yselect = yearSelect2(2013, date("Y"), "year1");
 $mselect = monthSelect(1, "month1");
 $dselect= daySelect2(1, "day1");
 $yselect2 = yearSelect2(2013, date("Y"), "year2");
 $mselect2 = monthSelect(date("m"), "month2");
 $dselect2= daySelect2(date("d"), "day2");

$sselect = "";
while( list($key,$val) = each($nt->table)){
	$sselect .= sprintf("<br /><input type=\"checkbox\" name=\"sts\" value=\"%s\">%s (%s County, %s)",
			$key, $val["name"], $val["county"], $key);
}

$soilopts = "";
$levels = Array(4,12,24,50);
while( list($key, $val) = each($levels)){
	$soilopts .= sprintf("<br /><input type=\"checkbox\" name=\"vars\" value=\"soil%02dtn\">Daily Low %s inch Soil Temperature [F]</input>\n"
		,$val, $val);
	$soilopts .= sprintf("<br /><input type=\"checkbox\" name=\"vars\" value=\"soil%02dt\">Daily Average %s inch Soil Temperature [F]</input>\n"
		,$val, $val);
	$soilopts .= sprintf("<br /><input type=\"checkbox\" name=\"vars\" value=\"soil%02dtx\">Daily High %s inch Soil Temperature [F]</input>\n"
			,$val, $val);
}

$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU Soil Moisture Network</a></li>
  <li class="active">Daily Download</li>
 </ol>

{$box}

<h3>Daily Data Request Form:</h3>

<P><b>Information:</b> This interface accesses the archive of daily weather 
data collected from 
the Iowa State Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 

<P><B>Data Interval:</B>Currently you are selected to download daily data. 
You may wish to change this to <a href="hourly.php">hourly data</a>. 


<form name="dl" method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="daily" />

<div class="row">
<div class="col-md-6">

<h4>Select station(s):</h4>
<a href="/sites/networks.php?network=ISUSM&format=html">View station metadata</a><br />
{$sselect}

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
<i>
When selecting the time interval, make sure you that choose <B> * valid * </B> dates.
</i>
<TABLE>
  <TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
  <TR><TH>Starting On:</TH>
 <TD>{$yselect}</TD>
 <td>{$mselect}</td>
 <td>{$dselect}</td>
 </tr>
</TR>
<TR><TH>Ending On:</TH>
 <TD>{$yselect2}</TD>
 <td>{$mselect2}</td>
 <td>{$dselect2}</td>
</TR>
</TABLE>

<h4>Options:</h4>

<strong>Select from available variables</strong><br />
<input type="checkbox" name="vars" value="high">High Temperature [F]
<br /><input type="checkbox" name="vars" value="low">Low Temperature [F]
<br /><input type="checkbox" name="vars" value="rh_min">Minimum Relative Humidity [%]
<br /><input type="checkbox" name="vars" value="rh">Average Relative Humidity [%]
<br /><input type="checkbox" name="vars" value="rh_max">Maximum Relative Humidity [%]
<br /><input type="checkbox" name="vars" value="gdd50">Growing Degree Days (base 50) [F]
<br /><input type="checkbox" name="vars" value="solar">Solar Radiation [MJ]
<br /><input type="checkbox" name="vars" value="precip">Precipitation [inch]
<br /><input type="checkbox" name="vars" value="sped">Average Wind Speed [mph]
<br /><input type="checkbox" name="vars" value="gust">Wind Gust [mph]
<br /><input type="checkbox" name="vars" value="et"> <a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [inch]
{$soilopts}
<br /><input type="checkbox" name="vars" value="soil12vwc">12 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil24vwc">24 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil50vwc">50 inch Soil Moisture [%]

<hr>
<p><strong>Vineyard Station-only Variables</strong>
<br />Sorry for the cryptic labels, this is a current work in progress.
<br /><input type="checkbox" name="vars" value="lwmv_1">lwmv_1
<br /><input type="checkbox" name="vars" value="lwmv_2">lwmv_2
<br /><input type="checkbox" name="vars" value="lwmdry_1_tot">lwmdry_1_tot
<br /><input type="checkbox" name="vars" value="lwmcon_1_tot">lwmcon_1_tot
<br /><input type="checkbox" name="vars" value="lwmwet_1_tot">lwmwet_1_tot
<br /><input type="checkbox" name="vars" value="lwmdry_2_tot">lwmdry_2_tot
<br /><input type="checkbox" name="vars" value="lwmcon_2_tot">lwmcon_2_tot
<br /><input type="checkbox" name="vars" value="lwmwet_2_tot">lwmwet_2_tot
<br /><input type="checkbox" name="vars" value="bpres_avg">bpres_avg

<p><strong>View on web browser or</strong> &nbsp; 
 <br /><input type="checkbox" name="todisk" value="yes">Download directly to disk

<p><strong>How should the data be formatted?:</strong> &nbsp; 
<select name="format">
	<option value="excel">Microsoft Excel (xlsx)</option>
	<option value="comma">Comma Delimited Text File</option>
  	<option value="tab">Tab Delimited Text File</option>
</select>

<p><h4>Submit your request:</h4>
	<input type="submit" value="Get Data">
	<input type="reset">

</form>

</div>
<div class="col-md-6">
<h4>Meaning of Data Columns</h4>
<dl class="dl-horizontal">
 <dt>station</dt><dd>National Weather Service Location Identifier for the
 site.  This is a five character identifier.</dd>
 		
 <dt>valid</dt><dd>Date of the observation</dd>

 <dt>high</dt><dd>High Temperature [F]</dd>
 <dt>low</dt><dd>Low Temperature [F]</dd>
 <dt>rh</dt><dd>Average Relative Humidity [%]</dd>
 <dt>rh_max</dt><dd>Maximum Relative Humidity based on hourly observations [%]</dd>
 <dt>rh_min</dt><dd>Minimum Relative Humidity based on hourly observations [%]</dd>
 <dt>gdd50</dt><dd>Growing Degree Days [F]</dd>
 <dt>solar</dt><dd>Solar Radiation [MJ/m^2]</dd>
 <dt>precip</dt><dd>Precipitation [inch]</dd>
 <dt>sped</dt><dd>Average Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
 <dt>gust</dt><dd>Peak Wind Gust [mph], 10 minute average, 10 ft above ground</dd>		
 <dt>et</dt><dd>Evapotranspiration [inch]</dd>
 <dt>soil04tn</dt><dd>Daily Low 4 inch Depth Soil Temperature [F]</dd>
 <dt>soil04t</dt><dd>Daily Average 4 inch Depth Soil Temperature [F]</dd>
 <dt>soil04tx</dt><dd>Daily High 4 inch Depth Soil Temperature [F]</dd>
 <dt>soil12tn</dt><dd>Daily Low 12 inch Depth Soil Temperature [F]</dd>
 <dt>soil12t</dt><dd>Daily Average 12 inch Depth Soil Temperature [F]</dd>
 <dt>soil12tx</dt><dd>Daily High 12 inch Depth Soil Temperature [F]</dd>
 <dt>soil24tn</dt><dd>Daily Low 24 inch Depth Soil Temperature [F]</dd>
 <dt>soil24t</dt><dd>Daily Average 24 inch Depth Soil Temperature [F]</dd>
 <dt>soil24tx</dt><dd>Daily High 24 inch Depth Soil Temperature [F]</dd>
 <dt>soil50tn</dt><dd>Daily Low 50 inch Depth Soil Temperature [F]</dd>
 <dt>soil50t</dt><dd>Daily Average 50 inch Depth Soil Temperature [F]</dd>
 <dt>soil50tx</dt><dd>Daily High 50 inch Depth Soil Temperature [F]</dd>
 <dt>soil12vwc</dt><dd>Average 12 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil24vwc</dt><dd>Average 24 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil50vwc</dt><dd>Average 50 inch Depth Soil Volumetric Water Content [%]</dd>
 		
 		
</dl>

</div></div>
EOF;
$t->render("single.phtml");
?>