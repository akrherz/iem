<?php
include("../../config/settings.inc.php");
include("../../include/forms.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "SMOS Data";
$t->thispage = "archive-smos";
$t->headextra = <<<EOF
<link rel='stylesheet' href='/assets/openlayers/2.13.1//theme/default/style.css' type='text/css'>
EOF;
$t->jsextra = <<<EOF
<script src='/assets/openlayers/2.13.1/OpenLayers.js'></script>
<script type='text/javascript'>
var controls;
var vectors;
var feature;
function init(){
	var proj = new OpenLayers.Projection('EPSG:4326');
				
	feature = new OpenLayers.Feature.Vector(
      	new OpenLayers.Geometry.Point(-10352712, 5160979),
 		{some:'data'},
 		{externalGraphic: '/images/marker.png', 
		graphicHeight: 21, graphicWidth: 16});
		
	vectors = new OpenLayers.Layer.Vector('Vector Layer');
	
		
		
    controls = {
        drag: new OpenLayers.Control.DragFeature(vectors, {
			onComplete: function(feature, pixel) {
				geo = feature.geometry.clone();
				geo.transform(map.getProjectionObject(), proj);
				document.getElementById('lon').value = geo.x;
				document.getElementById('lat').value = geo.y;
}
		})
    };
      var map = new OpenLayers.Map({
          div: 'map',
          theme: null,
          layers: [
              new OpenLayers.Layer.OSM('OpenStreetMap', null, {
                  transitionEffect: 'resize'
              }), vectors
          ],
          zoom: 1
      });
      for(var key in controls) {
          map.addControl(controls[key]);
			controls[key].activate();
		}
		map.setCenter(new OpenLayers.LonLat(-93.0, 42.0).transform(
        	proj, map.getProjectionObject()), 5);
		
		vectors.addFeatures(feature);
}
</script>
<style type='text/css'>
        #map {
            width: 100%;
            height: 200px;
            border: 2px solid black;
        }
</style>
EOF;
$t->bodyextra = "onload=\"init();\"";

$y1select = yearSelect2(2012, 2010, "year1");
$m1select = monthSelect2(1, "month1");
$d1select = daySelect2(1, "day1");

$y2select = yearSelect2(2012, 2010, "year2");
$m2select = monthSelect2(1, "month2");
$d2select = daySelect2(1, "day2");

$t->content = <<<EOF
<h3>Soil Moisture &amp; Ocean Salinity (SMOS) Satellite Data</h3>

<p>The <a href="http://www.esa.int/SPECIALS/smos/">SMOS</a> satellite is a polar
orbiting satellite operated by the European Space Agency.  The satellite provides
estimates of soil moisture in the approximate top 5 centimeters of soil and the
amount of vegetation on the land surface.  
<a href="mailto:bkh@iastate.edu">Dr Brian Hornbuckle</a> leads a 
<a href="http://bkh.public.iastate.edu/research/index.html">local research
team</a> here at Iowa State that works with this data.  The IEM collects processed
data from this satellite, generates analysis plots, and makes the raw data available.

<h4>Download Data</h4>
<p>This form allows you to download a single grid cell's worth of data based on 
the latitude and longitude pair you provide.  Data is only available here from 
the Midwestern United States.  The form will provide an error if you attempt
to request a point outside of the domain.  Data is available since 
<strong>12 Jan 2010</strong>.<br />
<form method="GET" action="dl.php" name="dl">
<div class="row"><div class="col-md-6">
<i>Enter Latitude/Longitude manually or drag marker on map to the right.</i>
<table>
<tr><th>Latitude (north degree)</th>
	<th><input id="lat" type="text" name="lat" size="6" value="42.0" /></th></tr>
<tr><th>Longitude (east degree)</th>
	<th><input id="lon" type="text" name="lon" size="6" value="-93.0" /></th></tr>
	</table>
<table>
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
  </tr>

  <tr>
    <th>Start:</th>
    <td>{$y1select}</td>
    <td>{$m1select}</td>
    <td>{$d1select}</td>
  </tr>

  <tr>
    <th>End:</th>
    <td>{$y2select}</td>
    <td>{$m2select}</td>
    <td>{$d2select}</td>
  </tr>
</table>
</div><div class="col-md-6">
<div id="map"></div>

    		</div></div>

<input type="submit" value="Get Data!" />
	
	</form>

<p><h4>Recent Analysis Plots</h4>
<i>Click image for archived imagery</i>
<table>
<tr>
<td><a href="/timemachine/#56.0"><img src="/data/smos_iowa_sm00.png" width="500" /></a></td>
<td><a href="/timemachine/#55.0"><img src="/data/smos_iowa_od00.png" width="500" /></a></td>
</tr>
<tr>
<td><a href="/timemachine/#53.0"><img src="/data/smos_midwest_sm00.png" width="500" /></a></td>
<td><a href="/timemachine/#53.0"><img src="/data/smos_midwest_od00.png" width="500"/></a></td>
</tr>
</table>
<br />
EOF;
$t->render('single.phtml');

?>
