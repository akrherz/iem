<?php
include("../../../config/settings.inc.php");
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";
 $hours = isset($_GET["hours"]) ? $_GET["hours"] : 24;
 $station = isset($_GET['station']) ? strtoupper( $_GET['station'] ): "";

include("$rootpath/include/database.inc.php");
include("$rootpath/include/google_keys.php");
include("$rootpath/include/imagemaps.php");
$api = $GOOGLEKEYS[$rooturl]["any"];
$HEADEXTRA = "<script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=$api'></script>
<script src='http://www.openlayers.org/api/OpenLayers.js'></script>
<script src='${rooturl}/js/olselect.php?network=${network}'></script>";
$BODYEXTRA = "onload=\"init()\"";

	$TITLE = "IEM | Time Series";
include("$rootpath/include/header.php"); 
?>
<style type="text/css">
        #map {
            width: 450px;
            height: 450px;
            border: 2px solid black;
        }
</style>
<br><br>
<div class="text">
<table width="100%">
<tr><td>

  <form method="GET" action="1station.php" name="olselect">
<?php
if (strlen($station) > 0 ) {

?>

  <?php echo networkSelect($network, $station); ?>
  <?php
    echo "<b>Options:</b>";
    echo " <b>|</b> <a href=\"1station.php?network=$network\">Select Visually</a><br> \n";
  ?>
  <select name="hours">
    <option value="24" <?php if ($hours == "24") echo "SELECTED"; ?>>24 hours
    <option value="48" <?php if ($hours == "48") echo "SELECTED"; ?>>48 hours
    <option value="72" <?php if ($hours == "72") echo "SELECTED"; ?>>72 hours
    <option value="96" <?php if ($hours == "96") echo "SELECTED"; ?>>96 hours
  </select>
  <input type="submit" value="Make Plot"></form>

</td></tr><tr bgcolor="#b2dfee"><td>

<BR><BR>


<img src="1temps.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
<BR>
<img src="winds.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
<br />
<img src="pres.php?hours=<?php echo $hours; ?>&station=<?php echo $station; ?>" ALT="Time Series">
</CENTER>

<BR>

<P>Data only valid within the past <?php echo $hours; ?> hours is displayed on this chart.

<P>Please take note of the timestamp labels.  The graph may have inconsistancies in it, if the series has 
missing data.

<BR><BR>
<?php } else { ?>
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
<?php echo networkSelect($network, $station); ?><input type="submit">
</form>


<?php } ?>

</td></tr></table>

<br><br></div>

<?php include("$rootpath/include/footer.php"); ?>
