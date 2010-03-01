<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | School Network | Download";
include("$rootpath/include/header.php");
include("$rootpath/include/forms.php");
 include("$rootpath/include/imagemaps.php"); 
?>

<h3 class="heading">SchoolNet Data Download</h3>

<div class="text">
<p>With this form, you can download schoolnet data.  The 
archive starts on <b>12 Feb 2002</b> for stations that were online at that
time.  You may want to consult a <a href="/schoolnet/history.php">listing</a>
of when the IEM started to archive data from a site.  Data from the current
day is not dumped into this archive until Midnight.  This means that the most
recent data is from yesterday.</p>

<form method="GET" action="worker.php">

<table>
<tr>
  <th class="subtitle">Select Station:</th>
  <td>
<?php echo snetSelectMultiple(" "); ?>
  </td>
</tr>

<tr>
  <th class="subtitle">Select <a href="/schoolnet/dl/params.php">Parameters</a></th>
  <td>
     <table>
     <tr>
       <td><input type="checkbox" name="vars[]" value="tmpf">Air Temperature</td>
       <td><input type="checkbox" name="vars[]" value="dwpf">Dew Point</td>
     </tr>
     <tr>
       <td><input type="checkbox" name="vars[]" value="drct">Wind Direction</td>
       <td><input type="checkbox" name="vars[]" value="sknt">Wind Speed</td>
     </tr>
     <tr>
       <td><input type="checkbox" name="vars[]" value="pday">Daily Precip Counter [2]</td>
       <td><input type="checkbox" name="vars[]" value="pmonth">Monthly Precip Counter [2]</td>
     </tr>
     <tr>
       <td><input type="checkbox" name="vars[]" value="srad">Solar Radiation</td>
       <td><input type="checkbox" name="vars[]" value="relh">Relative Humidity</td>
     </tr>
     <tr>
       <td><input type="checkbox" name="vars[]" value="alti" colspan=2>Altimeter (Pressure)</td>
     </tr>
     </table>
  </td>
</tr>

<tr>
  <th class="subtitle">Time Interval:</th>
  <td>
    <table>
     <tr>
      <td></td>
      <th class="subtitle">Year:</th>
      <th class="subtitle">Month:</th>
      <th class="subtitle">Day:</th>
      <th class="subtitle">Hour:</th>
     </tr>
     <tr>
      <th class="subtitle">Start:</th>
      <th>
<?php echo yearSelect2(2002, date("Y"), "year1"); ?>
      </th>
      <td>
<?php echo monthSelect(date("m"), "month1"); ?>
      </td>
      <td>
<?php echo daySelect2(date("d"), "day1"); ?>
</td>
      <td>
<?php echo hourSelect(0, "hour1"); ?>
</td>
     </tr>
     <tr>
      <th class="subtitle">End:</th>
      <th>
<?php echo yearSelect2(2002, date("Y"), "year2"); ?>
      </th>
      <td>
<?php echo monthSelect(date("m"), "month2"); ?>
      </td>
      <td>
<?php echo daySelect2(date("d"), "day2"); ?>
</td>
      <td>
<?php echo hourSelect(0, "hour2"); ?>
</td>
     </tr>
    </table>
  </td>
</tr>

<tr>
  <th class="subtitle">Data Sampling: [1]</th>
  <td>
  <select name="sample">
    <option value="1min">Every Minute
    <option value="5min">Every 5 Minutes
    <option value="10min">Every 10 Minutes
    <option value="20min">Every 20 Minutes
    <option value="1hour">Every Hour
  </select>
  </td>
</tr>

<tr>
  <th class="subtitle">Download Options</th>
  <td>
   <select name="dl_option">
    <option value="download">Download to disk
    <option value="view">View on-line
   </select>
  </td>
</tr>

<tr>
  <th class="subtitle">Delimitation</th>
  <td>
   <select name="delim">
    <option value="comma">Comma
    <option value="space">Space
    <option value="tab">Tab
   </select>
  </tr>
</tr>

<tr>
  <td colspan="2" align="CENTER">
  <input type="submit" value="Download Data">
  <input type="reset">
</td>
</tr>

</table>

</form>

<p><b>1. </b> For this archive, data is saved every minute.  In most cases, 
you will not be interested in data at that temporal frequency.  You can adjust
the sampling to cut down on the amount of data.
<br><b>2. </b> Precipitation is measured by a non-heated tipping bucket.  Thus
cold season precipitation is not accurately measured.
<br><b>3. </b> Wind data before 4 August 2002 were instantaneous values.
Wind data afterwards are 1 minute average values.

<br></div>
<?php include("$rootpath/include/footer.php"); ?>
