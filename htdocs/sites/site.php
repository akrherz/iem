<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");
$THISPAGE="iem-sites";
$TITLE = sprintf("IEM | Site Info | %s %s", $station, $cities[$station]["name"]);
$HEADEXTRA = '<script src="https://maps.googleapis.com/maps/api/js?sensor=false" type="text/javascript"></script>';
include("$rootpath/include/header.php");
?>
<?php $current = "base"; include("sidebar.php"); ?>

<div style="float: left;">


<table><tr><td valign="top">

<table cellpadding='1' border='1' cellspacing='0'>
<tr><th>Station Identifier:</th><td><?php echo $station; ?></td></tr>
<tr><th>Station Name:</th><td><?php echo $cities[$station]["name"]; ?></td></tr>
<tr><th>Network:</th><td><?php echo $network; ?></td></tr>
<tr><th>County:</th><td><?php echo $cities[$station]["county"]; ?></td></tr>
<tr><th>State:</th><td><?php echo $cities[$station]["state"]; ?></td></tr>
<tr><th>Latitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["lat"]); ?></td></tr>
<tr><th>Longitude:</th><td><?php echo sprintf("%.5f", $cities[$station]["lon"]); ?></td></tr>
<tr><th>Elevation [m]:</th><td><?php echo $cities[$station]["elevation"]; ?></td></tr>
<tr><th>Time Zone:</th><td><?php echo $cities[$station]["tzname"]; ?></td></tr>
</table>

</td><td>
  <div id="mymap" style="height: 640px; width: 640px;"></div>
</td>
</tr></table>

</div>
<script type="text/javascript">
var map;
function load(){
    var mapOptions = {
            zoom: 15,
            center: new google.maps.LatLng(<?php echo sprintf("%.5f", $cities[$station]["lat"]); ?>, <?php echo sprintf("%.5f", $cities[$station]["lon"]); ?>),
            mapTypeId: google.maps.MapTypeId.ROADMAP
          };
    map = new google.maps.Map(document.getElementById('mymap'),
              mapOptions);
  	
 
 	var mysite = new google.maps.Marker({position: mapOptions.center,
 	 	map: map});
}
google.maps.event.addDomListener(window, 'load', load);

</script>
<?php include("$rootpath/include/footer.php"); ?>
