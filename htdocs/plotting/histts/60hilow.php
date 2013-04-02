<?php 
include("../../../config/settings.inc.php");
$station = isset($_GET["station"]) ? $_GET["station"] : "";
$network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

include("$rootpath/include/database.inc.php");
include("$rootpath/include/imagemaps.php");
$HEADEXTRA = "<script src='https://maps.googleapis.com/maps/api/js?sensor=false'></script>
<script src='http://openlayers.org/api/2.12/OpenLayers.js'></script>
<script src='${rooturl}/js/olselect.php?network=${network}'></script>";
$BODYEXTRA = "onload=\"init()\"";

$TITLE = "IEM | Last 60 days High Low";
include("$rootpath/include/header.php");
?>
<style type="text/css">
        #map {
            width: 450px;
            height: 450px;
            border: 2px solid black;
        }
</style>


<P>Back to <a href="/plotting/index.php">Interactive Plotting</a>.


<?php
if (strlen($station) > 0 ) {

?>
<CENTER>
<BR><BR>
<P><a href="60hilow.php">Different Location</a>
<P>
<BR><BR>

<img src="60hilow_plot.php?station=<?php echo $station; ?>" ALT="Time Series">

</CENTER>

<BR>

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php
} else {
?>
<form name="olselect">
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
<?php echo networkSelect($network, ""); ?><input type="submit" value="Go!">
</form>

<?php
}
?>

<?php include("$rootpath/include/footer.php"); ?>
