<?php 
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 65);
require_once "../../../include/myview.php";
require_once "../../../include/iemprop.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";
require_once "../../../include/network.php";

$t = new MyView();
$t->title = "AWOS One Minute Data Download";

$awos_archive_end = strtotime( get_iemprop("awos.1min.end") );
$bogus = 0;

$ys1 = yearSelect2(1995, date("Y"), "year1");
$ms1 = monthSelect($bogus, "month1");
$ds1 = daySelect2($bogus, "day1");
$mi1 = minuteSelect($bogus, "minute1"); 
$hs1 = hour24Select($bogus, "hour1");

$ys2 = yearSelect2(1995, date("Y"), "year2");
$ms2 = monthSelect($bogus, "month2");
$ds2 = daySelect2($bogus, "day2");
$mi2 = minuteSelect($bogus, "minute2");
$hs2 = hour24Select($bogus, "hour2");

$aend = date('d M Y', $awos_archive_end);

$nt = new NetworkTable("IA_ASOS");
$ar = Array();
foreach ($nt->table as $sid => $meta){
    if (array_key_exists("IS_AWOS", $meta["attributes"])){
        $ar[$sid] = $meta["name"];
    }
}

$sselect = make_select('station', "", $ar, '', '', TRUE, TRUE);

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/AWOS/">AWOS Network</a></li>
 <li class="active">Download One Minute Data</li>
</ol>

<p>The Iowa Department of Transportation (DOT) manages the 
network of AWOS sensors in the state of Iowa.  While 20 minute interval data
is published to the world in real-time, they also collect one minute interval
data internally.  Each month, the DOT kindly provides us with the previous
month's archive of one minute data.  We process this data into our database
and make the observations available here for download.  Please don't make
giant data requests through this interface, instead feel 
free to email Daryl (akrherz@iastate.edu) and make your request.</p>

<div class="alert alert-warning">Population of this archive was discontinued by the DOT on 1 April 2011. Data
for dates after that date can be found 
<a class="link link-warning" href="/request/download.phtml?network=IA_ASOS">here</a>, but it is only
at a 20 minute interval.

<ul>
 <li><b>Archive Begins:</b> 1 Jan 1995 (for some sites, not all)</li>
 <li><b>Last Date in Archive:</b> {$aend} </li>
</ul>
</div>
<form method="GET" action="1min_dl.php" name="dl">

<div class="row">
<div class="col-md-6 col-sm-6">

<p><h3 class="subtitle">1. Select Station:</h3><br>
<i>Select One or More or All stations in the network. Clinton and Fort Dodge 
where converted to ASOS in September of 2000.  Data for these sites exists 
in this archive up until that point.</i><br>
{$sselect}

<p><h3>2. Select Start/End Time:</h3><br>
<strong>Time Zone:</strong><input type="radio" value="UTC" name="tz" checked="checked"> UTC  
<input type="radio" value="local" name="tz">Local CST/CDT

<table>
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th><th>Minute</th>
  </tr>

  <tr>
    <th>Start:</th>
    <td>{$ys1}</td><td>{$ms1}</td><td>{$ds1}</td><td>{$hs1}</td><td>{$mi1}</td></tr>
  <tr>
    <th>End:</th>
    <td>{$ys2}</td><td>{$ms2}</td><td>{$ds2}</td><td>{$hs2}</td><td>{$mi2}</td></tr>
</table>

<p><h3 class="subtitle">3. Select Variables:</h3><br>
(<i><a href="/AWOS/skyc.phtml">More information</a> about cloud coverage codes.</i>)
<select size=5 name="vars[]" MULTIPLE>
  <option value="tmpf">Air Temperature
  <option value="dwpf">Dew Point Temperature
  <option value="sknt">Wind Speed [knots]
  <option value="drct">Wind Direction
  <option value="gust">Wind Gust [knots]
  <option value="vsby">Visibility
  <option value="p01i">Hourly Precipitation Accumulator
  <option value="alti">Altimeter
  <option value="cl1">Cloud Deck 1 Height
  <option value="ca1">Cloud Deck 1 Coverage
  <option value="cl2">Cloud Deck 2 Height
  <option value="ca2">Cloud Deck 2 Coverage
  <option value="cl3">Cloud Deck 3 Height
  <option value="ca3">Cloud Deck 3 Coverage
</select>

</div>
<div class="col-md-6 col-sm-6">


<p><h3 class="subtitle">4. Data Sampling?</h3><br>
<i>Data is potentially available every minute, but you don't have to download
it at that frequency. This setting <b>does not bin</b> the values, but rather
filters based on your interval of choice.</i>
  <select name="sample">
    <option value="1min">Every Minute
    <option value="5min">Every 5 Minutes
    <option value="10min">Every 10 Minutes
    <option value="20min">Every 20 Minutes
    <option value="1hour">Every Hour
  </select>

<p><h3 class="subtitle">5. How to view?</h3><br>
<select name="what">
  <option value="download">Download to Disk
  <option value="view">View on-line
</select>

<p><h3 class="subtitle">6. Data Delimitation:</h3><br>
How shall the output values be seperated?
<br><select name="delim">
    <option value="comma">Comma
    <option value="space">Space
    <option value="tab">Tab
   </select>

<p>
<h3 class="subtitle">7. Include Station Latitude & Longitude values?</h3><img src="/images/gisready.png"><br>
<div class="story">
 <select name="gis">
   <option value="no">No
   <option value="yes">Yes
 </select>
</div>

</div>

<p><h3>Submit Form:</h3><br>
<input type="submit" value="Process Data Request">
<input type="reset">
</form>
EOM;
$t->render('single.phtml');
