<?php 
include("../../config/settings.inc.php");

$HEADEXTRA = '
<script src="https://maps.googleapis.com/maps/api/js?sensor=false" type="text/javascript"></script>
<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.4.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.4.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.4.0/ext-all.js"></script>
<script type="text/javascript" src="wfos.js?v=3"></script>
<script type="text/javascript" src="Exporter-all.js"></script>
<script type="text/javascript" src="search.js?v=6"></script>
		  <style>
  #map {
    width: 500px;
    height: 400px;
    float: left;
  }
		#warntable { float: right; }
		</style>
		';
$THISPAGE ="severe-vtec";
$TITLE = "IEM | NWS Warning Search by Point or County/Zone";
include("$rootpath/include/header.php");
?>

<p>This application allows you to search for National Weather Service Watch,
Warning, and Advisories.  There are currently two options:

<h3>1. Search for Storm Based Warnings by Point</h3>

<br />The official warned area for some products the NWS issues is a polygon.
This section allows you to specify a point on the map below by dragging the 
marker to where you are interested in.  Once you stop dragging the marker, the
grid will update and provide a listing of storm based warnings found.  
<br clear="all" />
<div id="map"></div>
<div id="warntable"></div>

<br clear="all" />
<h3>2. Search for NWS Watch/Warning/Advisories Products by County/Zone</h3>
<br />
<p>The NWS issues watch, warnings, and advisories (WWA) for counties/parishes.  For 
some products (like winter warnings), they issue for forecast zones.  In many parts of the country, these zones are exactly the 
same as the counties/parishes.  When you get into regions with topography, then zones will start to 
differ to the local counties.</p>
<br />
<p>This application allows you to search the IEM's archive of NWS WWA products.  Our archive is not complete, but
there are no known holes since 12 November 2005.  This archive is of those products that contain VTEC codes, which
are nearly all WWAs that the NWS issues for. </p>
<br />
<p><strong>Please note:</strong> NWS forecast offices have 
changed over the years, this application may incorrectly label old warnings as coming from
an office that did not exist at the time.</p>
<br />
<div id="myform"></div>
<br />
<p>The table will automatically populate below once you make your selections above. Click on the linked Event ID
to get more information on the warning.</p>
<br />
<div id="mytable"></div>

<?php include("$rootpath/include/footer.php"); ?>
