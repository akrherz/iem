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


include("$rootpath/include/database.inc.php");
include("$rootpath/include/google_keys.php");
include("$rootpath/include/imagemaps.php");
$api = $GOOGLEKEYS[$rooturl]["any"];
$HEADEXTRA = "<script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=$api'></script>
<script src='http://www.openlayers.org/api/OpenLayers.js'></script>
<script src='${rooturl}/js/olselect.php?network=${network}'></script>";
$BODYEXTRA = "onload=\"init()\"";
$TITLE = "IEM | Historical Time Series";
include("$rootpath/include/header.php"); 

?>
<style type="text/css">
        #map {
            width: 450px;
            height: 450px;
            border: 2px solid black;
        }
</style>
<form name="olselect">
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
} else {

?>

<BR><BR>
<P><a href="pickts.php">Different ASOS/AWOS Location</a>
<BR><a href="pickts.php?network=rwis">Different RWIS Location</a>
<P>
<BR>

<TABLE>
<TR>
	<TH>Station:</TH>
	<TH>Select Year:</TH>
	<TH>Select Month:</TH>
	<TH>Select Day:</TH>
	<TH>Select Starting Hour:</TH>
	<TH>Select Duration:</TH>
</TR>

<TR>
<td><?php echo networkSelect($network, $station); ?></td>
<TD>
<?php yearSelect2(2001, $year, "year"); ?>
</TD>

<TD><?php echo monthSelect($month); ?></TD>

<TD><?php echo daySelect($day); ?></td>

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
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
</form>

<?php
}
?>

</div>

<?php include("$rootpath/include/footer.php"); ?>
