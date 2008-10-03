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
      <th rowspan=2>
<?php echo yearSelect(2002, "year"); ?>
      </th>
      <td>
<?php echo monthSelect(date("m"), "month1"); ?>
      </td>
      <td>
<select name="s_day">
<?php
  for ($i=1; $i<32; $i++){
    echo "<option value=\"".$i."\">".$i ."\n";
  }
?>
</select>
</td>
      <td>
<select name="s_hour">
  <option value="0">12 AM
  <option value="1">1 AM
  <option value="2">2 AM
  <option value="3">3 AM
  <option value="4">4 AM
  <option value="5">5 AM
  <option value="6">6 AM
  <option value="7">7 AM
  <option value="8">8 AM
  <option value="9">9 AM
  <option value="10">10 AM
  <option value="11">11 AM
  <option value="12">Noon
  <option value="13">1 PM
  <option value="14">2 PM
  <option value="15">3 PM
  <option value="16">4 PM
  <option value="17">5 PM
  <option value="18">6 Pm
  <option value="19">7 PM
  <option value="20">8 PM
  <option value="21">9 PM
  <option value="22">10 PM
  <option value="23">11 PM
  <option value="24">Midnight
</select>
</td>
     </tr>
     <tr>
      <th class="subtitle">End:</th>
<td>
<?php echo monthSelect(date("m"), "month2"); ?>
</td>
      <td>
<select name="e_day">
<?php
  for ($i=1; $i<32; $i++){
    echo "<option value=\"".$i."\">".$i ."\n";
  }
?>
</select>
      </td>
      <td>
<select name="e_hour">
  <option value="0">12 AM
  <option value="1">1 AM
  <option value="2">2 AM
  <option value="3">3 AM
  <option value="4">4 AM
  <option value="5">5 AM
  <option value="6">6 AM
  <option value="7">7 AM
  <option value="8">8 AM
  <option value="9">9 AM
  <option value="10">10 AM
  <option value="11">11 AM
  <option value="12">Noon
  <option value="13">1 PM
  <option value="14">2 PM
  <option value="15">3 PM
  <option value="16">4 PM
  <option value="17">5 PM
  <option value="18">6 PM
  <option value="19">7 PM
  <option value="20">8 PM
  <option value="21">9 PM
  <option value="22">10 PM
  <option value="23">11 PM
  <option value="24">Midnight
</select>
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
