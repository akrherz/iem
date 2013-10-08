<?php 
 /* Daily Data download for the ISUAG Network */ 
 include("../../../config/settings.inc.php");
 $TITLE = "IEM | ISU Agclimate | Daily Data Request";
 $THISPAGE="networks-agclimate";
 include("../../../include/network.php");
 $nt = new NetworkTable("ISUSM");
 include("../../../include/header.php"); 
 include("../../../include/forms.php");
?>
<h3 class="heading">Daily Data Request Form:</h3>
<div class="text">
<P><b>Information:</b> This interface accesses the archive of daily weather 
data collected from 
the Iowa State Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 

<P><B>Data Interval:</B>Currently you are selected to download daily data. 
You may wish to change this to <a href="hourly.php">hourly data</a>. 


<form name="dl" method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="daily" />

<table width="100%">
<tr><td valign="top">

<h4 class="subtitle">Select station(s):</h4>
<?php 
while( list($key,$val) = each($nt->table)){
  echo sprintf("<br /><input type=\"checkbox\" name=\"sts\" value=\"%s\">%s (%s)",
	$key, $val["name"], $key);
}
?>

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
<i>
When selecting the time interval, make sure you that choose <B> * valid * </B> dates.
</i>
<TABLE>
  <TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
  <TR><TH>Starting On:</TH>
    <TD><?php echo yearSelect2(1986, date("Y"), "year1"); ?></TD>
   <td><?php echo monthSelect(1, "month1"); ?></td>
 <td><?php echo daySelect2(1, "day1"); ?></td>
 </tr>
</TR>
<TR><TH>Ending On:</TH>
 <TD><?php echo yearSelect2(1986, date("Y"), "year2"); ?></TD>
 <td><?php echo monthSelect(date("m"), "month2"); ?></td>
 <td><?php echo daySelect2(date("d"), "day2"); ?></td>
</TR>
</TABLE>

<h4 class="subtitle">Options:</h4>
<input type="checkbox" name="todisk" value="yes">Download directly to disk
<br>How should the values be separated?: 
<select name="delim">
  <option value="comma">by commas
  <option value="tab">by tabs
</select>

<p><b><h4 class="subtitle">Submit your request:</h4></b>
	<input type="submit" value="Get Data">
	<input type="reset">

</form></div>

</td><td valign="top">

<dl>
 <dt>station</dt><dd>National Weather Service Location Identifier for the
 site.  This is a five character identifier.</dd>
 <dt>valid</dt><dd>Timestamp of the observation either in CST or CDT</dd>
 </dl>

</td></tr>

</table>

<?php include("../../../include/footer.php"); ?>
