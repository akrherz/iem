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

$yselect = yearSelect2(2013, date("Y"), "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect2(1, "day1");
$yselect2 = yearSelect2(2013, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect2(date("d"), "day2");

$sselect = "";
foreach ($nt->table as $key => $val) {
    $sselect .= sprintf(
        '<br /><input type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label for="%s">%s (%s County, %s)</label>',
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
        '<br /><input type="checkbox" name="vars" value="soil%02dtn" ' .
            'id="soil%02dtn"> <label for="soil%02dtn">' .
            'Daily Low %s inch Soil Temperature [F]</label>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
    $soilopts .= sprintf(
        '<br /><input type="checkbox" name="vars" value="soil%02dt" ' .
            'id="soil%02dt"> <label for="soil%02dt">' .
            'Daily Average %s inch Soil Temperature [F]</label>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
    $soilopts .= sprintf(
        '<br /><input type="checkbox" name="vars" value="soil%02dtx" ' .
            'id="soil%02dtx"> <label for="soil%02dtx">' .
            'Daily High %s inch Soil Temperature [F]</label>' . "\n",
        $val,
        $val,
        $val,
        $val
    );
}

$t->content = <<<EOF
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU Soil Moisture Network</a></li>
  <li class="active">Daily Download</li>
 </ol>

{$box}

<h3>Daily Data Request Form:</h3>

<p><b>Information:</b> This interface accesses the archive of daily weather 
data collected from 
the Iowa State Agclimate Automated Weather stations.  Please
select the stations and weather variables desired below.</p>

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
<input type="checkbox" name="vars" value="high" id="high">
 <label for="high">High Temperature [F]</label>
<br /><input type="checkbox" name="vars" value="low" id="low">
 <label for="low">Low Temperature [F]</label>
<br /><input type="checkbox" name="vars" value="chillhours" id="chillhours">
 <label for="chillhours">Daily Chill Hours,</label>
 Base (&deg;F): <input type="text" size="3" value="32" name="chillbase">
 Ceiling (&deg;F): <input type="text" size="3" value="45" name="chillceil">
<br /><input type="checkbox" name="vars" value="rh_min" id="rh_min">
 <label for="rh_min">Minimum Relative Humidity [%]</label>
<br /><input type="checkbox" name="vars" value="rh" id="rh">
 <label for="rh">Average Relative Humidity [%]</label>
<br /><input type="checkbox" name="vars" value="rh_max" id="rh_max">
 <label for="rh_max">Maximum Relative Humidity [%]</label>
<br /><input type="checkbox" name="vars" value="gdd50" id="gdd50">
 <label for="gdd50">Growing Degree Days (base 50) [F]</label>
<br /><input type="checkbox" name="vars" value="solar" id="solar">
 <label for="solar">Solar Radiation [J/m^2]</label>
 <br /><input type="checkbox" name="vars" value="solar_mj" id="solar_mj">
 <label for="solar_mj">Solar Radiation [MJ/m^2]</label>
<br /><input type="checkbox" name="vars" value="precip" id="precip">
 <label for="precip">Precipitation [inch]</label>
<br /><input type="checkbox" name="vars" value="speed" id="speed">
 <label for="speed">Average Wind Speed [mph]</label>
<br /><input type="checkbox" name="vars" value="gust" id="gust">
 <label for="gust">Wind Gust [mph]</label>
<br /><input type="checkbox" name="vars" value="et" id="et">
 <label for="et">Reference Evapotranspiration [inch]</label> <a href="/agclimate/et.phtml" target="_new">More Info</a>
{$soilopts}
<br /><input type="checkbox" name="vars" value="soil12vwc" id="soil12vwc">
 <label for="soil12vwc">12 inch Soil Moisture [%]</label>
<br /><input type="checkbox" name="vars" value="soil24vwc" id="soil24vwc">
 <label for="soil24vwc">24 inch Soil Moisture [%]</label>
<br /><input type="checkbox" name="vars" value="soil50vwc" id="soil50vwc">
 <label for="soil50vwc">50 inch Soil Moisture [%]</label>

<hr>
<p><strong>Vineyard Station-only Variables</strong>
<br />Sorry for the cryptic labels, this is a current work in progress.
<br /><input type="checkbox" name="vars" value="lwmv_1" id="lwmv_1">
 <label for="lwmv_1">lwmv_1</label>
<br /><input type="checkbox" name="vars" value="lwmv_2" id="lwmv_2">
 <label for="lwmv_2">lwmv_2</label>
<br /><input type="checkbox" name="vars" value="lwmdry_1_tot" id="lwmdry_1_tot">
 <label for="lwmdry_1_tot">lwmdry_1_tot</label>
<br /><input type="checkbox" name="vars" value="lwmcon_1_tot" id="lwmcon_1_tot">
 <label for="lwmcon_1_tot">lwmcon_1_tot</label>
<br /><input type="checkbox" name="vars" value="lwmwet_1_tot" id="lwmwet_1_tot">
 <label for="lwmwet_1_tot">lwmwet_1_tot</label>
<br /><input type="checkbox" name="vars" value="lwmdry_2_tot" id="lwmdry_2_tot">
 <label for="lwmdry_2_tot">lwmdry_2_tot</label>
<br /><input type="checkbox" name="vars" value="lwmcon_2_tot" id="lwmcon_2_tot">
 <label for="lwmcon_2_tot">lwmcon_2_tot</label>
<br /><input type="checkbox" name="vars" value="lwmwet_2_tot" id="lwmwet_2_tot">
 <label for="lwmwet_2_tot">lwmwet_2_tot</label>
<br /><input type="checkbox" name="vars" value="bpres_avg" id="bpres_avg">
 <label for="bpres_avg">bpres_avg</label>

<hr>
<p>The Ames-AEA, Ames-Kitchen, and Jefferson locations have the
<a href="https://www.campbellsci.com/soilvue10">CS SoilVue 10</a> installed.<br />

<input type="checkbox" name="vars" value="sv" id="sv">
<label for="sv">SoilVue Temperature + Moisture Data</label>
</p>

{$qcbox}

<p><strong>View on web browser or</strong> &nbsp; 
 <br /><input type="checkbox" name="todisk" value="yes" id="todisk">
  <label for="todisk">Download directly to disk</label>

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
 <dt>solar</dt><dd>Solar Radiation [J/m^2]</dd>
 <dt>precip</dt><dd>Precipitation [inch]</dd>
 <dt>speed</dt><dd>Average Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
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
