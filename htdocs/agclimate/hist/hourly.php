<?php
 include("../../../config/settings.inc.php");
 $TITLE = "ISU Agclimate | Data Request";
 $THISPAGE="networks-agclimate";
 include("../../../include/network.php");
 $nt = new NetworkTable("ISUSM");
 include("../../../include/header.php");
 include("../../../include/forms.php");
?>

<h3 class="heading">Hourly Data Request Form:</h3>
<div class="text">
<P><b>Information:</b>  This interface accesses the archive of daily and hourly weather
data collected from the Iowa Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 


<P><B>Data Interval:</B>  Currently you are selected to download hourly data. You may
wish to change this to <a href="daily.php">daily data</a>. 


<table><tr><td valign="top">

<form name='dl' method="GET" action="/cgi-bin/request/isusm.py">
<input type="hidden" name="mode" value="hourly" />

<h4 class="subtitle">Select station(s):</h4>
<?php 
while( list($key,$val) = each($nt->table)){
  echo sprintf("<br /><input type=\"checkbox\" name=\"sts\" value=\"%s\">%s (%s)",
	$key, $val["name"], $key);
}
?>


<p><b><h4 class="subtitle">Select the time interval:</h4></b>
		<TABLE>
				<TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
				<TR><TH>Starting On:</TH>
 <TD><?php echo yearSelect2(2012, date("Y"), "year1"); ?></TD>
 <td><?php echo monthSelect2(1, "month1"); ?></td>
 <td><?php echo daySelect2(1, "day1"); ?></td>
				</TR>
				<TR><TH>Ending On:</TH>
<TD><?php echo yearSelect2(2012, date("Y"), "year2"); ?></TD>
 <td><?php echo monthSelect2(date("m"), "month2"); ?></td>
 <td><?php echo daySelect2(date("d"), "day2"); ?></td>
				</TR>
			</TABLE>

<p><b><h4 class="subtitle">Options:</h4></b>
<input type="checkbox" name="todisk" value="yes">Download directly to disk
<br>Delimination: <select name="delim">
  <option value="comma">Comma Delimited
  <option value="tab">Tab Delimited
</select>

<p><b><h4 class="subtitle">Submit your request:</h4></b>
	<input type="submit" value="Submit Query">
	<input type="reset">

</form></div>

</td><td valign="top">

<h4 class="subtitle">Description of variables in download</h4>

<dl>
 <dt>station</dt><dd>National Weather Service Location Identifier for the
 site.  This is a five character identifier.</dd>
 <dt>valid</dt><dd>Timestamp of the observation either in CST or CDT</dd>
 <dt>tmpf</dt><dd>Air Temperature</dd>
 </dl>

</td></tr>

</table>


<?php include("../../../include/footer.php"); ?>
