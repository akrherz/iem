<?php 
 /* 
  * Download front end for daily data from the ISUSM network
  */
 require_once "../../../config/settings.inc.php";
 require_once "../../../include/myview.php";
 $t = new MyView();
 $t->title = "ISU Soil Moisture Hourly Data Request";
 
 require_once "../../../include/network.php";
 $nt = new NetworkTable("ISUSM");
 require_once "../../../include/forms.php";
 require_once "boxinc.phtml";
 
 $yselect = yearSelect2(2013, 2013, "year1");
 $mselect = monthSelect(1, "month1");
 $dselect= daySelect2(1, "day1");
 $yselect2 = yearSelect2(2013, date("Y"), "year2");
 $mselect2 = monthSelect(date("m"), "month2");
 $dselect2= daySelect2(date("d"), "day2");

$sselect = "";
foreach($nt->table as $key => $val)
{
	$sselect .= sprintf("<br /><input type=\"checkbox\" name=\"sts\" value=\"%s\">%s (%s County, %s)",
			$key, $val["name"], $val["county"], $key);
}
 
$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU Soil Moisture Network</a></li>
  <li class="active">Hourly Download</li>
 </ol>

{$box}

<h3>Hourly Data Request Form:</h3>

<P><b>Information:</b>  This interface accesses the archive of daily and hourly weather
data collected from the Iowa Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 


<P><B>Data Interval:</B>  Currently you are selected to download hourly data. You may
wish to change this to <a href="daily.php">daily data</a>. 


<div class="row">
<div class="col-md-6">

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="hourly" />

<h4>Select Time Resolution:</h4>

<select name="timeres">
  <option value="hourly">Hourly</option>
  <option value="minute">Minute (coming soon!)</option>
</select>

<h4>Select station(s):</h4>
<a href="/sites/networks.php?network=ISUSM&format=html">View station metadata</a><br />
{$sselect}


<h4>Select the time interval:</h4>
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
<input type="checkbox" name="vars" value="tmpf">Air Temperature [F]
<br /><input type="checkbox" name="vars" value="relh">Relative Humidity [%]
<br /><input type="checkbox" name="vars" value="solar">Solar Radiation [J]
<br /><input type="checkbox" name="vars" value="precip">Precipitation [inch]
<br /><input type="checkbox" name="vars" value="speed">Average Wind Speed [mph]
<br /><input type="checkbox" name="vars" value="drct">Wind Direction [deg]
<br /><input type="checkbox" name="vars" value="et"> <a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a> [inch]
<br /><input type="checkbox" name="vars" value="soil04t">4 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil12t">12 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil24t">24 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil50t">50 inch Soil Temperature [F]
<br /><input type="checkbox" name="vars" value="soil12vwc">12 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil24vwc">24 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="soil50vwc">50 inch Soil Moisture [%]
<br /><input type="checkbox" name="vars" value="bp_mb">Atmospheric Pressure [mb] (only Ames ISU Hort Farm at 15 minute interval)

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
 		
{$qcbox}

<p><input type="checkbox" name="todisk" value="yes">Download directly to disk

 <p><strong>How should the data be formatted?:</strong> &nbsp; 
<select name="format">
	<option value="excel">Microsoft Excel (xlsx)</option>
	<option value="comma">Comma Delimited Text File</option>
  	<option value="tab">Tab Delimited Text File</option>
</select>

<p><strong>How should missing values be represented?:</strong>
<br /> 
<select name="missing">
	<option value="-99">-99</option>
	<option value="M">M</option>
  	<option value="">(blank, empty space)</option>
</select>

<p><b><h4 class="subtitle">Submit your request:</h4></b>
	<input type="submit" value="Submit Query">
	<input type="reset">

</form>

</div><div class="col-md-6">

<h4 class="subtitle">Description of variables in download</h4>

<dl>
 <dt>station</dt><dd>National Weather Service Location Identifier for the
 site.  This is a five character identifier.</dd>
 <dt>valid</dt><dd>Timestamp of the observation either in CST or CDT</dd>
 <dt>tmpf</dt><dd>Air Temperature [F]</dd>
 <dt>relh</dt><dd>Relative Humidity [%]</dd>
 <dt>solar</dt><dd>Solar Radiation [Joules]</dd>
 <dt>precip</dt><dd>One Hour Precipitation [inch]</dd>
 <dt>sped</dt><dd>Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
 <dt>drct</dt><dd>Wind Direction [degrees North], 10 minute average, 10 ft above ground</dd>
 <dt>et</dt><dd>Potential Evapotranspiration (Alfalfa) [inch]</dd>
 <dt>soil04t</dt><dd>4 inch Depth Soil Temperature [F]</dd>
 <dt>soil12t</dt><dd>12 inch Depth Soil Temperature [F]</dd>
 <dt>soil24t</dt><dd>24 inch Depth Soil Temperature [F]</dd>
 <dt>soil50t</dt><dd>50 inch Depth Soil Temperature [F]</dd>
 <dt>soil12vwc</dt><dd>12 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil24vwc</dt><dd>24 inch Depth Soil Volumetric Water Content [%]</dd>
 <dt>soil50vwc</dt><dd>50 inch Depth Soil Volumetric Water Content [%]</dd>
 
 </dl>

 		</div></div>

EOF;
$t->render("single.phtml");
?>