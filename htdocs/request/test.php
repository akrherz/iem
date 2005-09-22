<html>
<!dOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
        <TITLE>IEM | Download Data</TITLE>

<script language="JavaScript">

function changeSite(newSite) {

	document.myForm.station.value = newSite ;

} // End of changeSite

</script>
	
</head>

<?php 
        $title = "IEM | Download Data";
        include("../include/header.php"); 
?>

<TR>
<TD width="100%" valign="top" colspan="5">


<body bgcolor="white">

<P>Back to <a href="/index.php">Mesonet Homepage</a>

<P>Please Complete each step to download data.

<form method="GET" action="/cgi-bin/request/getData.py" name="myForm">

<TABLE>
<TR>
<TD valign="top">
<b>1) Select Station/Network by clicking on location: </b>
<BR> &nbsp; &nbsp; <i>(Station identifier will appear on right side)</i>
<?php 
	include("../include/imagemaps2.php"); 
	if (strlen($network) == 0){
   		echo "<BR><a href=\"test.php?network=rwis\">Switch to RWIS</a>\n";
         	print_asos("bah");
	} else {
		echo "<BR><a href=\"test.php\">Switch to ASOS/AWOS</a>\n";
		print_rwis("bah");
	}
?>


</TD>

<TD>
<P>Selected Station: <input type="text" name="station" size="5">
<br> &nbsp; &nbsp; <i>(Either enter site ID or select graphically)</i>

<P>
<B>2) Select From Available Data:</B>
<BR><SELECT name="data" size="5" MULTIPLE>
	<option value="all" SELECTED>All Available
	<option value="tmpf">Air Temperature
	<option value="dwpf">Dew Point
	<option value="drct">Wind Direction 
	<option value="sknt">Wind Speed
<?php if (strlen($network) == 0) { ?>
	<option value="skyc">Cloud Coverage
	<option value="p01m">1 hour Precipitation
	<option value="alti">Altimeter
<?php } ?>
</SELECT>

<P>
<b>3) Select Date Range:</b>
<BR><SELECT name="timeRange"> 
	<Option value="allYear">Entire Year
	<option value="allMonth">Entire Month
	<option value="rangeMonth">Range of Months
	<option value="allDay">Entire Day
	<option value="rangeDays">Range of Days
</SELECT>

<P>
<b>4) Specific Date Range (If needed):</b>
<BR><TABLE>
<TR><TH>Start:</TH><TH>Stop:</TH></TR>

<TR>
 <TD colspan="2" align="center">
  <SELECT name="year">
	<option value="1979">1979
	<option value="1995">1995
	<option value="1996">1996
	<option value="1997">1997
	<option value="1998">1998
	<option value="1999">1999
	<option value="2000">2000
	<option value="2001">2001
	<option value="2002">2002
	<option value="2003">2003
  </SELECT>
 </TD>
</TR>

<TR>
 <TD>
   <SELECT name="month1">
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
   </SELECT>
 </TD>
 <TD>
    <SELECT name="month2">
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
   </SELECT>
 </TD>
</TR>

<tr>
 <td>
  <SELECT name="day1">
   <option value="1">1	 <option value="2">2	 <option value="3">3	 <option value="4">4
   <option value="5">5	 <option value="6">6	 <option value="7">7	 <option value="8">8
   <option value="9">9	 <option value="10">10   <option value="11">11   <option value="12">12
   <option value="13">13   <option value="14">14   <option value="15">15   <option value="16">16
   <option value="17">17   <option value="18">18   <option value="19">19   <option value="20">20
   <option value="21">21   <option value="22">22   <option value="23">23   <option value="24">24
   <option value="25">25   <option value="26">26   <option value="27">27   <option value="28">28
   <option value="29">29   <option value="30">30   <option value="31">31
  </SELECT>
 </td>
 <td>
  <SELECT name="day2">
   <option value="1">1	 <option value="2">2	 <option value="3">3	 <option value="4">4
   <option value="5">5	 <option value="6">6	 <option value="7">7	 <option value="8">8
   <option value="9">9	 <option value="10">10   <option value="11">11   <option value="12">12
   <option value="13">13   <option value="14">14   <option value="15">15   <option value="16">16
   <option value="17">17   <option value="18">18   <option value="19">19   <option value="20">20
   <option value="21">21   <option value="22">22   <option value="23">23   <option value="24">24
   <option value="25">25   <option value="26">26   <option value="27">27   <option value="28">28
   <option value="29">29   <option value="30">30   <option value="31">31
  </SELECT>
 </td>

</tr>

</TABLE>

<P>
<b>5) Include possible 20min observations?</b>
<br><i> &nbsp; &nbsp; (Leave yes if unsure)</i>
<SELECT name="include20s">
	<option value="yes">Yes
	<option value="no">No
</SELECT>

<P>
<b>6) Format of time output:</b>
<br><SELECT name="tz">
	<option value="GMT">GMT (UTC) timestamps
	<option value="local">Central Standard/Daylight Time
</SELECT>

<p>
<b>7) Data Format:</b>
<br><SELECT name="format">
	<option value="tdf">Tab Delimited
	<option value="space">Space Delimited
	<option value="comma">Comma Delimited
</SELECT>

<p>
<b>8) Finally, get Data:</b>
<br>
  <input type="submit" value="Get Data">
  <input type="reset">
</TD></TR></TABLE>
</form>

</TD></TR>

<?php include("../include/footer.html"); ?>

