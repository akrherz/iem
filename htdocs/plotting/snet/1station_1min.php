<?php 
 include("../../../config/settings.inc.php");
 include('../../schoolnet/switchtv.php'); 
 include("$rootpath/include/forms.php");
 include("$rootpath/include/imagemaps.php"); 
 include("$rootpath/include/google_keys.php"); 

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$station = isset($_GET['station'] ) ? $_GET['station'] : "";

?>

<?php 
if (! isset($_GET["station"])){
  include("$rootpath/include/google_keys.php");
  $network = $tv;
  $api = $GOOGLEKEYS[$rooturl]["any"];
  $HEADEXTRA = "<script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=$api'></script>
 <script src='http://www.openlayers.org/api/OpenLayers.js'></script>
 <script src='${rooturl}/js/olselect.php?network=${network}'></script>";
 $BODYEXTRA = "onload=\"init()\"";
}
$TITLE = "IEM | 1 Minute Time Series";
$THISPAGE = "networks-schoolnet"; 
include("$rootpath/include/header.php"); 
?>
<h3>1 minute data interval time series</h3>

<p>This application generates graphs of 1 minute interval data 
for a school based network of your choice. Note that the archive
begins on 12 February 2002, but does not go back that far for 
every site.</p>


<form method="GET" action="1station_1min.php" name="olselect">
<input type="hidden" name="ntv" value="<?php echo $tv; ?>"> 
  <?php
    echo " <a href=\"1station_1min.php\">Select Visually</a><br> \n";
    echo "Make plot selections: ";
    echo networkSelect($tv, $station); 

  ?>
   <?php yearSelect2(2002, $year, "year"); ?>
 <?php echo monthSelect($month); ?>
 <?php daySelect($day); ?>

  <input type="submit" value="Make Plot"></form>

<?php
if (strlen($station) > 0 ) {

echo sprintf("<p><img src=\"1min_T.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day); 
echo sprintf("<p><img src=\"1min_V.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day); 
echo sprintf("<p><img src=\"1min_P.php?station=%s&year=%s&month=%s&day=%s\" />", $station, $year, $month, $day); 

echo "<p><b>Note:</b> The wind speeds are indicated every minute by the red line.  The blue dots represent wind direction and are shown every 10 minutes.</p>";

} else {
?>

<p>or select from this map...<p>

<?php 
 $link = '1station_1min.php';
 include('../../schoolnet/switchbar.php'); ?>

<style type="text/css">
        #map {
            width: 640px;
            height: 400px;
            border: 2px solid black;
        }
</style>
<i>Click black dot to select your site:</i><br />
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>


<?php  } ?>

</td></tr></table>
</td></tr></table>

<?php include("$rootpath/include/footer.php"); ?>
