<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";
force_https();
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "setup.php";
require_once "../../include/iemprop.php";
$gmapskey = get_iemprop("google.maps.key");

$alertmsg = "";
if (isset($_GET["lat"]) &&
		$_GET["lat"] != "move marker" &&
		floatval($_GET["lat"]) != 0 &&
		floatval($_GET["lat"]) != 1 &&
		floatval($_GET["lat"]) != -1 &&
		floatval($_GET["lon"]) != 0 &&
		floatval($_GET["lon"]) != 1 &&
		floatval($_GET["lon"]) != -1){
	$newlat = floatval($_GET["lat"]);
	$newlon = floatval($_GET["lon"]);
	$email = isset($_GET["email"]) ? xssafe($_GET["email"]): 'n/a';
	$name = isset($_GET["name"]) ? xssafe($_GET["name"]): "n/a";
	$msg = <<<EOF
IEM Sites Move Request
======================
> REMOTE_ADDR: {$_SERVER["REMOTE_ADDR"]}
> ID:          {$station}
> NAME:        {$name} OLD: {$cities[$station]["name"]}
> NETWORK:     {$network}
> LON:         {$newlon} OLD: {$cities[$station]["lon"]}
> LAT:         {$newlat} OLD: {$cities[$station]["lat"]}
> EMAIL:       {$email}

https://mesonet.agron.iastate.edu/sites/site.php?network={$network}&station={$station}
EOF;
	mail("akrherz@iastate.edu", "Please move {$station} {$network}", $msg);
	$alertmsg = "<div class=\"alert alert-danger\">Thanks! Your suggested move was submitted for evaluation.</div>";
}

$t = new MyView();
$t->thispage="iem-sites";
$t->title = sprintf("Site Info: %s %s", $station, $cities[$station]["name"]);
$t->headextra = <<<EOF
<script src="https://maps.googleapis.com/maps/api/js?key={$gmapskey}" type="text/javascript"></script>
EOF;
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

<a href="networks.php?station={$station}&amp;network={$network}" class="btn btn-primary"><span class="fa fa-menu-hamburger"></span> View {$network} Network Table</a>

</div>
<div class="col-md-8">

  <div id="mymap" style="height: 400px; width: 100%;"></div>
 <div>
 <strong>Location Feedback:</strong> Do you believe the shown location to be
 incorrect?  If so, please consider moving the marker on the map to the proper
 location and submitting this form for review.
	<form name="updatecoords" method="GET">
	<input type="hidden" value="{$network}" name="network">
	<input type="hidden" value="{$station}" name="station">
	New Latitude: <input id="newlat" type="text" size="10" name="lat" placeholder="move marker">
	New Longitude: <input id="newlon" type="text" size="10" name="lon" placeholder="move marker">
	<br />Enter Your Email Address [1]: <input type="text" size="40" name="email" placeholder="optional">
	<br />Better Location Name?: <input type="text" name="name" value="{$cities[$station]["name"]}" />
	<br />[1] Your email address will not be shared nor will you be added to any
	lists. The IEM developer will simply email you back after consideration of
	this request.
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