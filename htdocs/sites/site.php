<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/google_keys.php");
include("setup.php");
$THISPAGE="iem-sites";
$TITLE = sprintf("IEM | Site Info | %s %s", $station, $cities[$station]["name"]);
$BODYEXTRA = "onload=\"javascript: load();\"";
$HEADEXTRA = '<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["any"] .'" type="text/javascript"></script>';
include("$rootpath/include/header.php");
?>
<?php $current = "base"; include("sidebar.php"); ?>

<div style="float: left;">


<table><tr><td valign="top">

<table>
<tr><th>Station Identifier:</th><td><?php echo $station; ?></td></tr>
<tr><th>Station Name:</th><td><?php echo $cities[$station]["name"]; ?></td></tr>
<tr><th>Network:</th><td><?php echo $network; ?></td></tr>
<tr><th>County:</th><td><?php echo $cities[$station]["county"]; ?></td></tr>
<tr><th>State:</th><td><?php echo $cities[$station]["state"]; ?></td></tr>
<tr><th>Latitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["lat"]); ?></td></tr>
<tr><th>Longitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["lon"]); ?></td></tr>
<tr><th>Elevation [m]:</th><td><?php echo $cities[$station]["elevation"]; ?></td></tr>
</table>

</td><td>
  <div id="mymap" style="height: 640px; width: 640px;"></div>
</td>
</tr></table>

</div>
<script type="text/javascript">
function load(){
 var mapSpecs = [];
 mapSpecs.push(G_NORMAL_MAP);
 mapSpecs.push(G_SATELLITE_MAP);
 mapSpecs.push(G_PHYSICAL_MAP);
 
 var mapdiv = document.getElementById("mymap");
 var map = new GMap2(mapdiv, { mapTypes: mapSpecs });
 var center = new GLatLng(<?php echo sprintf("%.5f", $cities[$station]["lat"]); ?>, <?php echo sprintf("%.5f", $cities[$station]["lon"]); ?>);
 map.setCenter(center, 17 - 2, G_SATELLITE_MAP);

 map.setUIToDefault();
 map.enableDoubleClickZoom();
 map.enableContinuousZoom();

 var mysite = new GMarker(center);
 map.addOverlay(mysite);
 
}
</script>
<?php include("$rootpath/include/footer.php"); ?>
