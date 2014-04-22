<?php 
 /* 
  * Download front end for daily data from the ISUSM network
  */
 include("../../../config/settings.inc.php");
 include("../../../include/myview.php");
 $t = new MyView();
 $t->title = "ISU Soil Moisture Daily Data Request";
 $t->thispage = "networks-agclimate";
 
 include("../../../include/network.php");
 $nt = new NetworkTable("ISUSM");
 include("../../../include/forms.php");

 $yselect = yearSelect2(2013, date("Y"), "year1");
 $mselect = monthSelect(date("m"), "month1");
 $dselect= daySelect2(date("d"), "day1");
 $yselect2 = yearSelect2(2013, date("Y"), "year2");
 $mselect2 = monthSelect(date("m"), "month2");
 $dselect2= daySelect2(date("d"), "day2");

$sselect = "";
while( list($key,$val) = each($nt->table)){
	$sselect .= sprintf("<br /><input type=\"checkbox\" name=\"sts\" value=\"%s\">%s (%s County, %s)",
			$key, $val["name"], $val["county"], $key);
}
 
$t->content = <<<EOF
<h3 class="heading">Daily Data Request Form:</h3>

<div class="alert alert-info">
This download page is for the recently installed (2013) ISU Soil Moisture sites.  
To download data from the legacy ISU AgClimate network, please visit 
<a class="alert-link" href="dailyRequest.php">this page</a>.
</div>

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
<br /><input type="checkbox" name="vars" value="solar">Solar Radiation [MJ]
<br /><input type="checkbox" name="vars" value="precip">Precipitation [inch]
<br /><input type="checkbox" name="vars" value="sped">Average Wind Speed [mph]
<br /><input type="checkbox" name="vars" value="gust">Wind Gust [mph]
<br /><input type="checkbox" name="vars" value="et">Potential Evapotranspiration[inch]
<br /><input type="checkbox" name="vars" value="soil04t">4 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil12t">12 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil24t">24 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil50t">50 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil12vwc">12 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil24vwc">24 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil50vwc">50 inch Soil Moisture [%]
 		
<p><strong>View on web browser or</strong> &nbsp; 
 <br /><input type="checkbox" name="todisk" value="yes">Download directly to disk

<p><strong>How should the values be separated?:</strong> &nbsp; 
<select name="delim">
  <option value="comma">by commas
  <option value="tab">by tabs
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
 <dt>solar</dt><dd>Solar Radiation [MJ/m^2]</dd>
 <dt>precip</dt><dd>Precipitation [inch]</dd>
 <dt>speed</dt><dd>Average Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
 <dt>gust</dt><dd>Peak Wind Gust [mph], 10 minute average, 10 ft above ground</dd>		
 <dt>et</dt><dd>Evapotranspiration [inch]</dd>
 <dt>soil04t</dt><dd>Average 4 inch Depth Soil Temperature [F]</dd>
 <dt>soil12t</dt><dd>Average 12 inch Depth Soil Temperature [F]</dd>
 <dt>soil24t</dt><dd>Average 24 inch Depth Soil Temperature [F]</dd>
 <dt>soil50t</dt><dd>Average 50 inch Depth Soil Temperature [F]</dd>
 <dt>soil12vwc</dt><dd>Average 12 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil24vwc</dt><dd>Average 24 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil50vwc</dt><dd>Average 50 inch Depth Soil Volumetric Water Content [%]</dd>
 		
 		
</dl>

</div></div>
EOF;
$t->render("single.phtml");
?>