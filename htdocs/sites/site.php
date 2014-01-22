<?php 
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("setup.php");

include("../../include/myview.php");
$t = new MyView();
$t->thispage="iem-sites";
$t->title = sprintf("Site Info: %s %s", $station, $cities[$station]["name"]);
$t->headextra = '<script src="https://maps.googleapis.com/maps/api/js?sensor=false" type="text/javascript"></script>';
$t->sites_current = "base";

$lat = sprintf("%.5f", $cities[$station]["lat"]);
$lon = sprintf("%.5f", $cities[$station]["lon"]);
$t->content = <<<EOF
<div style="float: left;">


<table><tr><td valign="top">

<table cellpadding='1' border='1' cellspacing='0'>
<tr><th>Station Identifier:</th><td>{$station}</td></tr>
<tr><th>Station Name:</th><td>{$cities[$station]["name"]}</td></tr>
<tr><th>Network:</th><td>{$network}</td></tr>
<tr><th>County:</th><td>{$cities[$station]["county"]}</td></tr>
<tr><th>State:</th><td>{$cities[$station]["state"]}</td></tr>
<tr><th>Latitude:</th><td>{$lat}</td></tr>
<tr><th>Longitude:</th><td>{$lon}</td></tr>
<tr><th>Elevation [m]:</th><td>{$cities[$station]["elevation"]}</td></tr>
<tr><th>Time Zone:</th><td>{$cities[$station]["tzname"]}</td></tr>
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
            center: new google.maps.LatLng({$lat}, {$lon}),
            mapTypeId: google.maps.MapTypeId.ROADMAP
          };
    map = new google.maps.Map(document.getElementById('mymap'),
              mapOptions);
  	
	mysite = new google.maps.Marker({position: mapOptions.center,
 	 	map: map});
}
google.maps.event.addDomListener(window, 'load', load);

</script>
EOF;
$t->render('sites.phtml');
?>