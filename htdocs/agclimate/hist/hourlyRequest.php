<?php
 include("../../../config/settings.inc.php");
 $TITLE = "ISU Agclimate | Data Request";
$THISPAGE="networks-agclimate";
 include("$rootpath/include/header.php");
 include("$rootpath/include/forms.php");
?>



<h3 class="heading">Hourly Data Request Form:</h3>
<div class="text">
<P><b>Information:</b>  This interface accesses the archive of daily and hourly weather
data collected from the Iowa Agclimate Automated Weather stations.  Please
select the appropiate stations and weather variables desired below. 


<P><B>Data Interval:</B>  Currently you are selected to download hourly data. You may
wish to change this to <a href="dailyRequest.php">daily data</a>. 



<form method="GET" action="worker.php">
<input type="hidden" name="startHour" value="0">

<table width="100%">
<tr><td valign="top">

<p><b><h4 class="subtitle">Select station(s):</h4></b>
	<input type="checkbox" name="sts[]" value="A130209">Ames<BR>
	<input type="checkbox" name="sts[]" value="A131069">Calmar<BR>
	<input type="checkbox" name="sts[]" value="A131299">Castana<BR>
	<input type="checkbox" name="sts[]" value="A131329">Cedar Rapids<BR>
	<input type="checkbox" name="sts[]" value="A131559">Chariton<BR>	
	<input type="checkbox" name="sts[]" value="A131909">Crawfordsville<BR>
  <input type="checkbox" name="sts[]" value="A130219">Gilbert<BR>
	<input type="checkbox" name="sts[]" value="A134309">Kanawha<BR>
	<input type="checkbox" name="sts[]" value="A134759">Lewis<BR>
	<input type="checkbox" name="sts[]" value="A135849">Muscatine<BR>
	<input type="checkbox" name="sts[]" value="A135879">Nashua<BR>
	<input type="checkbox" name="sts[]" value="A136949">Rhodes<BR>
	<input type="checkbox" name="sts[]" value="A138019">Sutherland<BR>

</td><td valign="top">

<p><b><h4 class="subtitle">Select data:</h4></b>
  <input type="checkbox" name="vars[]" value="c100">Air Temperature [F]<BR>
  <input type="checkbox" name="vars[]" value="c800">Solar Radiation Values [kilo calorie per meter squared]<BR>
  <input type="checkbox" name="vars[]" value="c900">Precipitation [inches]<BR>
  <input type="checkbox" name="vars[]" value="c300">4 inch Soil Temperatures [F]<BR>
  <input type="checkbox" name="vars[]" value="c200">Relative Humidity [%]<BR>
  <input type="checkbox" name="vars[]" value="c400">Wind Speed [MPH]<BR>
  <input type="checkbox" name="vars[]" value="c600">Wind Direction [deg]<BR>

</td></tr></table>

<p><b><h4 class="subtitle">Select the time interval:</h4></b>
		<TABLE>
				<TR><TH></TH><TH>Year:</TH><TH>Month:</TH><TH>Day:</TH></TR>
				<TR><TH>Starting On:</TH>
 <TD><?php echo yearSelect2(1986, date("Y"), "startYear"); ?></TD>
				<td><SELECT name="startMonth">
					<option value="1">January
					<option value="2">February
					<option value="3">March
					<option value="4">April
					<option value="5">May
					<option value="6">June
					<option value="7">July
					<option value="8">August
					<option value="9">September
					<option value="10">October
					<option value="11">November
					<option value="12">December
				</SELECT></td>
				<td><SELECT name="startDay">
					<option value="1">1	<option value="2">2	<option value="3">3	<option value="4">4
					<option value="5">5	<option value="6">6	<option value="7">7	<option value="8">8
					<option value="9">9	<option value="10">10	<option value="11">11	<option value="12">12
					<option value="13">13	<option value="14">14	<option value="15">15	<option value="16">16
					<option value="17">17	<option value="18">18	<option value="19">19	<option value="20">20
					<option value="21">21	<option value="22">22	<option value="23">23	<option value="24">24
					<option value="25">25	<option value="26">26	<option value="27">27	<option value="28">28
					<option value="29">29	<option value="30">30	<option value="31">31
				</SELECT></td>
				</TR>
				<TR><TH>Ending On:</TH>
<TD><?php echo yearSelect2(1986, date("Y"), "endYear"); ?></TD>
				<td><SELECT name="endMonth">
					<option value="1">January
					<option value="2">Febuary
					<option value="3">March
					<option value="4">April
					<option value="5">May
					<option value="6">June
					<option value="7">July
					<option value="8">August
					<option value="9">September
					<option value="10">October
					<option value="11">November
					<option value="12">December
				</SELECT></td>
				<td><SELECT name="endDay">
					<option value="1">1	<option value="2">2	<option value="3">3	<option value="4">4
					<option value="5">5	<option value="6">6	<option value="7">7	<option value="8">8
					<option value="9">9	<option value="10">10	<option value="11">11	<option value="12">12
					<option value="13">13	<option value="14">14	<option value="15">15	<option value="16">16
					<option value="17">17	<option value="18">18	<option value="19">19	<option value="20">20
					<option value="21">21	<option value="22">22	<option value="23">23	<option value="24">24
					<option value="25">25	<option value="26">26	<option value="27">27	<option value="28">28
					<option value="29">29	<option value="30">30	<option value="31">31
				</SELECT></td>
				</TR>
			</TABLE>

<p><b><h4 class="subtitle">Options:</h4></b>
<input type="checkbox" name="qcflags" value="yes">Include QC Flags
<br><input type="checkbox" name="todisk" value="yes">Download directly to disk
<br>Delimination: <select name="delim">
  <option value="comma">Comma Delimited
  <option value="tab">Tab Delimited
</select>

<br />Text file format:
<select name="lf">
  <option value="dos">Windows/DOS
  <option value="unix">UNIX/MacOSX
</select>


<p><b><h4 class="subtitle">Submit your request:</h4></b>
	<input type="submit" value="Submit Query">
	<input type="reset">

<BR><BR>
</form></div>

<?php include("$rootpath/include/footer.php"); ?>
