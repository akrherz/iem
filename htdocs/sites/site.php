<?php 
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/myview.php");

include("setup.php");

$alertmsg = "";
if (isset($_GET["lat"]) && $_GET["lat"] != "move marker"){
	$newlat = floatval($_GET["lat"]);
	$newlon = floatval($_GET["lon"]);
	$msg = <<<EOF
{$_SERVER["REMOTE_ADDR"]} suggests moving $station [{$network}] to
{$newlon} {$newlat}
EOF;
	mail("akrherz@iastate.edu", "Please move {$station} {$network}", $msg);
	$alertmsg = "<div class=\"alert alert-danger\">Thanks! Your suggested move was submitted for evaluation.</div>";
}

$t = new MyView();
$t->thispage="iem-sites";
$t->title = sprintf("Site Info: %s %s", $station, $cities[$station]["name"]);
$t->headextra = '<script src="https://maps.googleapis.com/maps/api/js?sensor=false" type="text/javascript"></script>';
$t->sites_current = "base";

$lat = sprintf("%.5f", $cities[$station]["lat"]);
$lon = sprintf("%.5f", $cities[$station]["lon"]);

$t->content = <<<EOF

{$alertmsg}

<div class="row">
<div class="col-md-4">

<table class="table table-condensed table-striped">
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

</div>
<div class="col-md-8">

  <div id="mymap" style="height: 400px; width: 100%;"></div>
 <div><strong>Location Wrong?:</strong> Current Lat:{$lat} Lon:{$lon} <br />
	<form name="updatecoords" method="GET">
	<input type="hidden" value="{$network}" name="network">
	<input type="hidden" value="{$station}" name="station">
	New Latitude: <input id="newlat" type="text" size="10" name="lat" value="move marker">
	New Longitude: <input id="newlon" type="text" size="10" name="lon" value="move marker">
	<input type="submit" value="Submit Update"></form>
</div>
</div>

<script type="text/javascript">
var map, marker;
function load(){
    var mapOptions = {
            zoom: 15,
            center: new google.maps.LatLng({$lat}, {$lon}),
            mapTypeId: google.maps.MapTypeId.ROADMAP
          };
    map = new google.maps.Map(document.getElementById('mymap'),
              mapOptions);
	marker = new google.maps.Marker({
            		position: mapOptions.center,
 	 				map: map,
					draggable: true
				});
    google.maps.event.addListener(marker, 'dragend', function() {
          displayCoordinates(marker.getPosition());
    });
            		
    //callback on when the marker is done moving    		
	function displayCoordinates(pnt) {
        var lat = pnt.lat();
        lat = lat.toFixed(8);
        var lng = pnt.lng();
		lng = lng.toFixed(8);
		$("#newlat").val(lat);
        $("#newlon").val(lng);
	}
}
google.maps.event.addDomListener(window, 'load', load);

</script>
EOF;
$t->render('sites.phtml');
?>