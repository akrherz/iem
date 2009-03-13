<?php 
include("../../../config/settings.inc.php");
$THISPAGE = "networks-awos";
$TITLE = "IEM | AWOS 1 Minute Data Download";
include("$rootpath/include/header.php"); 
include_once("$rootpath/include/constants.php");
$bogus = 0;
?>

<div class="text">
<b>Nav:</b> <a href="/AWOS/">AWOS</a> <b> > </b>
  Download Data

<p>The Iowa Department of Transportation (DOT) manages the 
network of AWOS sensors in the state of Iowa.  While 20 minute interval data
is published to the world in real-time, they also collect one minute interval
data internally.  Each month, the DOT kindly provides us with the previous
month's archive of one minute data.  We process this data into our database
and make the observations available here for download.  Please don't make
giant data requests through this interface, instead feel free to email Daryl (akrherz@iastate.edu) and make your request.</p>

<p><b>Archive complete till:</b> <?php echo date('d M Y', $awos_archive_end); ?></p>

<?php include("$rootpath/include/imagemaps.php"); ?>
<?php include("$rootpath/include/forms.php"); ?>

<p>


<form method="GET" action="1min_dl.php">

<table>
<tr><td width="50%">

<p><h3 class="subtitle">1. Select Station:</h3><br>
<i>Select One or More or All stations in the network. Clinton and Fort Dodge 
where converted to ASOS in September of 2000.  Data for these sites exists 
in this archive up until that point.</i><br>
<div class="story">
  <?php awosMultiSelect("", 5); ?>
</div>

<p><h3 class="subtitle">2. Select Start/End Time:</h3><br>
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
    <td rowspan="2">
     <?php echo yearSelect(1995, date("Y"), "year"); ?>
    </td>
    <td>
     <?php echo monthSelect($bogus, "month1"); ?>
    </td>
    <td>
     <?php echo daySelect2($bogus, "day1"); ?>
    </td>
    <td>
     <?php echo hour24Select($bogus, "hour1"); ?>
    </td>
    <td>
     <?php echo minuteSelect($bogus, "minute1"); ?>
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     <?php echo monthSelect($bogus, "month2"); ?>
    <td>
     <?php echo daySelect2($bogus, "day2"); ?>
    </td>
    <td>
     <?php echo hour24Select($bogus, "hour2"); ?>
    </td>
    <td>
     <?php echo minuteSelect($bogus, "minute2"); ?>
    </td>
  </tr>
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

</td><td valign="TOP">

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
  <option value="plot">Plot in Chart
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

</td></tr></table>

<p><h3 class="subtitle">Submit Form:</h3><br>
<input type="submit" value="Process Data Request">
<input type="reset">
</form>
</div>

<?php include("$rootpath/include/footer.php"); ?>
