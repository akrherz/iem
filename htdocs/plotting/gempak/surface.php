<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
     "http://www.w3.org/TR/html4/loose.dtd"> 
<HTML>
<HEAD>
	<TITLE>IEM | Historical Time Series</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/main.css">
</HEAD>

<?php 
	$title = "IEM | Historical Time Series";
	include("../../include/header.php"); 
?>

<TR>

<?php include("../../include/side.html"); ?>
<?php include("../../include/imagemaps.php"); ?>

<TD width="450" valign="top">
<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.

<blockquote>This application plots a timeseries of temperature and dew point for a station 
of your choice</blockquote>

<?php
if (strlen($station) > 0 && strlen($month) > 0 ) {
?>
<P><a href="surface.php">Different ASOS/AWOS Location</a>
<BR><a href="surface.php?network=rwis">Different RWIS Location</a>
<BR><a href="surface.php?station=<?php echo $station; ?>">Different Time</a>



<?php
} elseif (strlen($station) > 0 && strlen($month) == 0 ) {

?>

<BR><BR>
<P><a href="surface.php">Different ASOS/AWOS Location</a>
<BR><a href="surface.php?network=rwis">Different RWIS Location</a>
<P>
<BR>

<FORM METHOD="GET" action="/cgi-bin/hist/plotter/wrapPlot.py">
<input type="hidden" name="station" value="<?php echo $station; ?>">
<TABLE>
<TR>
	<TH>Select Year:</TH>
	<TH>Select Month:</TH>
	<TH>Select Day:</TH>
	<TH>Select Starting Hour:</TH>
	<TH>Select Duration:</TH>
</TR>

<TR>
<TD>
<SELECT name="year">
        <option value="2001">2001
</SELECT>
</TD>

<TD>
<SELECT name="month">
        <option value="06">June 
	<option value="07">July 
        <option value="08">August 
        <option value="09">September 
	<option value="10">October
	<option value="11">November
	<option value="12">December
</SELECT>
</TD>

<TD>
<SELECT name="day">
        <option value="01">1	<option value="02">2	<option value="03">3	<option value="04">4
        <option value="05">5	<option value="06">6     <option value="07">7	<option value="08">8  
        <option value="09">9	<option value="10">10 	<option value="11">11	<option value="12">12
        <option value="13">13     <option value="14">14	<option value="15">15     <option value="16">16
        <option value="17">17     <option value="18">18	<option value="19">19     <option value="20">20
        <option value="21">21     <option value="22">22	<option value="23">23   <option value="24">24
        <option value="25">25     <option value="26">26	<option value="27">27     <option value="28">28
        <option value="29">29     <option value="30">30	<option value="31">31
 
</SELECT>
</TD>

<TD>
<SELECT name="hour">
        <option value="00">00Z     <option value="01">01Z     <option value="02">02Z     <option value="03">03Z
        <option value="04">04Z	<option value="05">05Z     <option value="06">06Z     <option value="07">07Z     <option value="08">08Z
        <option value="09">09Z     <option value="10">10Z   <option value="11">11Z   <option value="12">12Z
        <option value="13">13Z     <option value="14">14Z <option value="15">15Z     <option value="16">16Z
        <option value="17">17Z     <option value="18">18Z <option value="19">19Z     <option value="20">20Z
        <option value="21">21Z     <option value="22">22Z <option value="23">23Z
</SELECT>
</TD>

<TD>
<SELECT name="minute">
        <option value="00">00
        <option value="20">20
        <option value="40">40
</SELECT>

</TD>

</TR>

</TABLE>
<P><INPUT type="submit" value="Generate Plot">
</FORM>


<BR><BR>
<?php
} elseif ( strlen($network) > 0 ) {
?>
<P>Please click on one of the stations in the map.
<BR>Or select a <a href="surface.php">AWOS/ASOS station</a>.

<?php
	echo print_rwis("surface.php?station");

} else {
?>
<P>Please click on one of the stations in the map.
<BR>Or select a <a href="pickts.php?network=rwis">RWIS station</a>.

<?php
	echo print_asos("surface.php?station");
}
?>



</TD></TR>

<?php include("../../include/footer.html"); ?>
