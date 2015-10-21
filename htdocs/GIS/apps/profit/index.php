<?php 
include_once "../../../../config/settings.inc.php";

include_once "../../../../include/myview.php";

$OL = "3.9.0";
$t = new MyView();
$t->title = "Profitability Map";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol3-layerswitcher.css" rel="stylesheet" />
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol3-layerswitcher.js'></script>
<script>
var map;
var player;
$(document).ready(function(){
	player = new ol.layer.Tile({
                        title: 'Profitability',
						visible: true,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2015/{z}/{x}/{y}.png'
                        })
                });
		
		map = new ol.Map({
                target: 'map',
                layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
                }), player],
		view: new ol.View({
                        projection: 'EPSG:3857',
					center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
		
                })
		});
    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

	$("#yearselect").buttonset();
	$( '#yearselect input[type=radio]').change(function(){
		player.setSource(new ol.source.XYZ({
			url : '/c/tile.py/1.0.0/profit'+this.value+'/{z}/{x}/{y}.png'
		}));
    });
});
</script>
EOF;

$t->content = <<<EOF
<style>
#legend{
    position:absolute; 
    top:4em; 
    left:10px; 
    z-index:10000; 
    background-color:#FFFFFF;
}
#yearselect{
	position:absolute; 
    top:0.5em; 
    left:60px; 
    z-index:10000; 
    background-color:#FFFFFF;	
}
</style>
<div style="width:100%; height:100%" id="map">
<div id="yearselect">
  <input type="radio" id="y2010" name="whichyear" value="2010"><label for="y2010">2010</label>
  <input type="radio" id="y2011" name="whichyear" value="2011"><label for="y2011">2011</label>
  <input type="radio" id="y2012" name="whichyear" value="2012"><label for="y2012">2012</label>
  <input type="radio" id="y2013" name="whichyear" value="2013"><label for="y2013">2013</label>
  <input type="radio" id="y2015" name="whichyear" value="2015" checked="checked"><label for="y2015">2015</label>
</div>
		
<div id="legend"><img src="profit_legend.png" /></div>		
</div>

EOF;

$t->render('app.phtml');

?>