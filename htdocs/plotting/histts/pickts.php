<?php 
include("../../../config/settings.inc.php");
	include("$rootpath/include/forms.php"); 

$station = isset($_GET["station"]) ? $_GET["station"]: "";
$network = isset($_GET["network"]) ? $_GET["network"]: "IA_ASOS";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");
$shour = isset($_GET["shour"]) ? $_GET["shour"]: 0;
$duration = isset($_GET["duration"])? $_GET["duration"]: 12;


 include("$rootpath/include/selectWidget.php");
 $sw = new selectWidget("pickts.php", "pickts.php?", $network);
 $sw->set_networks( Array("IA_ASOS","AWOS","IA_RWIS") );
 $sw->logic($_GET);

$TITLE = "IEM | Historical Time Series";
include("$rootpath/include/header.php"); 

?>


<?php include("$rootpath/include/imagemaps.php"); ?>

<div class="text">
<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.<p>

This application plots a timeseries of temperature and dew point for a station 
of your choice

<?php
if (strlen($station) > 0 && strlen($month) > 0 ) {
?>
<P><a href="pickts.php">Different ASOS/AWOS Location</a>
<BR><a href="pickts.php?network=IA_RWIS">Different RWIS Location</a>
<BR><a href="pickts.php?station=<?php echo $station; ?>">Different Time</a>

<P>
<img src="pickts_plot.php?shour=<?php echo $shour; ?>&day=<?php echo $day; ?>&year=<?php echo $year; ?>&month=<?php echo $month; ?>&station=<?php echo $station; ?>&duration=<?php echo $duration; ?>" ALT="Time Series">
<BR>
<img src="winds.php?shour=<?php echo $shour; ?>&day=<?php echo $day; ?>&year=<?php echo $year; ?>&month=<?php echo $month; ?>&station=<?php echo $station; ?>&duration=<?php echo $duration; ?>" ALT="Time Series">


<P>View <a href="pickts_raw.php?shour=<?php echo $shour; ?>&day=<?php echo $day; ?>&year=<?php echo $year; ?>&month=<?php echo $month; ?>&station=<?php echo $station; ?>&duration=<?php echo $duration; ?>">raw</a> data.


<?php
} elseif (strlen($station) > 0 && strlen($month) == 0 ) {

?>

<BR><BR>
<P><a href="pickts.php">Different ASOS/AWOS Location</a>
<BR><a href="pickts.php?network=rwis">Different RWIS Location</a>
<P>
<BR>

<FORM METHOD="GET" action="pickts.php">
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
<?php yearSelect2(2001, $year, "year"); ?>
</TD>

<TD>
<SELECT name="month">
	<option value="1">January
	<option value="2">Feburary
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
<SELECT name="day">
        <option value="1">1	<option value="2">2	<option value="3">3	<option value="4">4
        <option value="5">5	<option value="6">6     <option value="7">7	<option value="8">8  
        <option value="9">9	<option value="10">10 	<option value="11">11	<option value="12">12
        <option value="13">13     <option value="14">14	<option value="15">15     <option value="16">16
        <option value="17">17     <option value="18">18	<option value="19">19     <option value="20">20
        <option value="21">21     <option value="22">22	<option value="23">23   <option value="24">24
        <option value="25">25     <option value="26">26	<option value="27">27     <option value="28">28
        <option value="29">29     <option value="30">30	<option value="31">31
 
</SELECT>
</TD>

<TD>
<SELECT name="shour">
        <option value="00">00Z     <option value="01">01Z     <option value="02">02Z     <option value="03">03Z
        <option value="04">04Z	<option value="05">05Z     <option value="06">06Z     <option value="07">07Z     <option value="08">08Z
        <option value="09">09Z     <option value="10">10Z   <option value="11">11Z   <option value="12">12Z
        <option value="13">13Z     <option value="14">14Z <option value="15">15Z     <option value="16">16Z
        <option value="17">17Z     <option value="18">18Z <option value="19">19Z     <option value="20">20Z
        <option value="21">21Z     <option value="22">22Z <option value="23">23Z
</SELECT>
</TD>

<TD>
<SELECT name="duration">
        <option value="12">12     
	<option value="24">24     
	<option value="36">36     
	<option value="48">48
</SELECT>
</TD>

</TR>

</TABLE>
<P><INPUT type="submit" value="Generate Plot">
</FORM>


<BR><BR>
<?php
} elseif ( strlen($network) > 0 ) {

echo $sw->printInterface();

}
?>

</div>

<?php include("$rootpath/include/footer.php"); ?>
