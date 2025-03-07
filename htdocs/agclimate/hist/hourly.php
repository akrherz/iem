<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

$t = new MyView();
$t->iem_resource = "ISUSM";
$t->title = "ISU Soil Moisture Minute/Hourly Data Request";

$nt = new NetworkTable("ISUSM");
require_once "boxinc.phtml";

$yselect = yearSelect2(2013, 2013, "year1");
$mselect = monthSelect(1, "month1");
$dselect = daySelect2(1, "day1");
$yselect2 = yearSelect2(2013, date("Y"), "year2");
$mselect2 = monthSelect(date("m"), "month2");
$dselect2 = daySelect2(date("d"), "day2");

$sselect = "";
foreach ($nt->table as $key => $val) {
    $sselect .= sprintf(
        '<br /><input type="checkbox" name="station" value="%s" id="%s"> ' .
            '<label for="%s">[%s] %s (%s County) (%s-%s)</label>',
        $key,
        $key,
        $key,
        $key,
        $val["name"],
        $val["county"],
        is_null($val["archive_begin"]) ? "" : $val["archive_begin"]->format("Y-m-d"),
        is_null($val["archive_end"]) ? "today" : $val["archive_end"]->format("Y-m-d"),
    );
}

$ar = array(
    "tmpf" => "Air Temperature [F]",
    "relh" => "Relative Humidity [%]",
    "solar" => "Solar Radiation [J/m2]",
    "precip" => "Precipitation [inch]",
    "speed" => "Average Wind Speed [mph]",
    "drct" => "Wind Direction [deg]",
    "et" => "Potential Evapotranspiration [inch]",
    "soil04t" => "4 inch Soil Temperature [F]",
    "soil12t" => "12 inch Soil Temperature [F]",
    "soil24t" => "24 inch Soil Temperature [F]",
    "soil50t" => "50 inch Soil Temperature [F]",
    "soil12vwc" => "12 inch Soil Moisture [%]",
    "soil24vwc" => "24 inch Soil Moisture [%]",
    "soil50vwc" => "50 inch Soil Moisture [%]",
    "bp_mb" => "Atmospheric Pressure [mb] (only Ames ISU Hort Farm at 15 minute interval)",
);
$vselect = make_checkboxes("vars", "", $ar);

$ar = array(
    "lwmv_1" => "lwmv_1",
    "lwmv_2" => "lwmv_2",
    "lwmdry_1_tot" => "lwmdry_1_tot",
    "lwmcon_1_tot" => "lwmcon_1_tot",
    "lwmwet_1_tot" => "lwmwet_1_tot",
    "lwmdry_2_tot" => "lwmdry_2_tot",
    "lwmcon_2_tot" => "lwmcon_2_tot",
    "lwmwet_2_tot" => "lwmwet_2_tot",
    "bpres_avg" => "bpres_avg",
);
$vselect2 = make_checkboxes("vars", "", $ar);

$t->content = <<<EOM
 <ol class="breadcrumb">
  <li><a href="/agclimate">ISU Soil Moisture Network</a></li>
  <li class="active">Minute/Hourly Download</li>
 </ol>

{$box}

<h3>Minute/Hourly Data:</h3>

<p>the present data collection interval from this network is every 15 minutes
for the vineyard sites and every minute for the others.  the minute interval
data only started in 2021 though.  The default download is to provide the
hourly data.</p>

<p><a href="/cgi-bin/request/isusm.py?help" class="btn btn-info">
<i class="fa fa-file"></i> Backend documentation</a> exists for those
wishing to script against this data service.</p>

<div class="row">
<div class="col-md-7">

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="hourly" />

<h4>Select Time Resolution:</h4>

<select name="timeres">
  <option value="hourly" selected="selected">Hourly</option>
  <option value="minute">Minute</option>
</select>

<h4>Select station(s):</h4>
<a href="/sites/networks.php?network=ISUSM">View station metadata</a><br />

{$sselect}

</div><div class="col-md-5">

<h4>Select the time interval:</h4>
<table>
  <tr><th></th><th>Year:</th><th>Month:</th><th>Day:</th></tr>
  <tr><th>Starting On:</th>
 <td>{$yselect}</td>
 <td>{$mselect}</td>
 <td>{$dselect}</td>
 </tr>
</tr>
<tr><th>Ending On:</th>
 <td>{$yselect2}</td>
 <td>{$mselect2}</td>
 <td>{$dselect2}</td>
</tr>
</table>


<h4>Options:</h4>

<strong>Select from available variables</strong><br />
<a href="/agclimate/et.phtml" target="_new">Reference Evapotranspiration (alfalfa)</a>

{$vselect}

<hr>
<p>The Ames-AEA, Ames-Kitchen, Ames-Hinds, and Jefferson locations have the
<a href="https://www.campbellsci.com/soilvue10">CS SoilVue 10</a> installed,
but the depth of installation varies by site with the first depth at
the Ames-AEA location being at 14 inches.<br />

<input type="checkbox" name="vars" value="sv" id="sv">
<label for="sv">All SoilVue Temperature + Moisture Data</label>

<br /><strong>or</strong> select from the following depths:<br />

<div class="row">
<div class="col-md-4">
<input type="checkbox" name="vars" value="sv2" id="sv2">
<label for="sv2">2 inch</label>
<br /><input type="checkbox" name="vars" value="sv12" id="sv12">
<label for="sv12">12 inch</label>
<br /><input type="checkbox" name="vars" value="sv20" id="sv20">
<label for="sv20">20 inch</label>
<br /><input type="checkbox" name="vars" value="sv30" id="sv30">
<label for="sv30">30 inch</label>
<br /><input type="checkbox" name="vars" value="sv40" id="sv40">
<label for="sv40">40 inch</label>
</div>

<div class="col-md-4">
<input type="checkbox" name="vars" value="sv4" id="sv4">
<label for="sv4">4 inch</label>
<br /><input type="checkbox" name="vars" value="sv14" id="sv14">
<label for="sv14">14 inch</label>
<br /><input type="checkbox" name="vars" value="sv24" id="sv24">
<label for="sv24">24 inch</label>
<br /><input type="checkbox" name="vars" value="sv32" id="sv32">
<label for="sv32">32 inch</label>
<br /><input type="checkbox" name="vars" value="sv42" id="sv42">
<label for="sv42">42 inch</label>
</div>

<div class="col-md-4">
<input type="checkbox" name="vars" value="sv8" id="sv8">
<label for="sv8">8 inch</label>
<br /><input type="checkbox" name="vars" value="sv16" id="sv16">
<label for="sv16">16 inch</label>
<br /><input type="checkbox" name="vars" value="sv28" id="sv28">
<label for="sv28">28 inch</label>
<br /><input type="checkbox" name="vars" value="sv36" id="sv36">
<label for="sv36">36 inch</label>
<br /><input type="checkbox" name="vars" value="sv52" id="sv52">
<label for="sv52">52 inch</label>
</div>

</div>

</p>

<hr>
<p><strong>Vineyard Station-only Variables</strong>

{$vselect2}

{$qcbox}

<p>
<input type="checkbox" name="todisk" value="yes" id="dd">
<label for="dd">Download directly to disk</label>
</p>

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

<p><strong>Timezone for Data:</strong>
<br />
<select name="tz">
    <option value="America/Chicago">Central Standard/Daylight Time</option>
    <option value="UTC">UTC</option>
</select></p>

<p><strong>Submit your request:</strong>
<br />
    <input type="submit" value="Submit">
    <input type="reset">

</form>


</div></div>

<h4>Description of variables in download</h4>

<dl>
 <dt>station</dt><dd>National Weather Service Location Identifier for the
 site.  this is a five character identifier.</dd>
 <dt>valid</dt><dd>Timestamp of the observation either in CST or CDT</dd>
 <dt>tmpf</dt><dd>Air Temperature [F]</dd>
 <dt>relh</dt><dd>Relative Humidity [%]</dd>
 <dt>solar</dt><dd>Solar Radiation [Joule/m2]</dd>
 <dt>precip</dt><dd>One Hour Precipitation [inch]</dd>
 <dt>speed</dt><dd>Wind Speed [mph], 10 minute average, 10 ft above ground</dd>
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

EOM;
$t->render("full.phtml");
