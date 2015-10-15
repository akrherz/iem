<?php 
include_once "../../../../config/settings.inc.php";

include_once "../../../../include/myview.php";

$t = new MyView();
$t->title = "Profitability Map";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/assets/openlayers/3.4.0/ol.css" type="text/css">
<link rel="stylesheet" href="/assets/jquery-ui/1.11.2/jquery-ui.min.css" />
<link type="text/css" href="/assets/openlayers/3.4.0/ol3-layerswitcher.css" rel="stylesheet" />
EOF;
$t->jsextra = <<<EOF
<script src="/assets/openlayers/3.4.0/ol.js" type="text/javascript"></script>
<script src="/assets/jquery-ui/1.11.2/jquery-ui.js"></script>
<script src='/assets/openlayers/3.4.0/ol3-layerswitcher.js'></script>
<script>
var map;
$(document).ready(function(){

		map = new ol.Map({
                target: 'map',
                layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
                }),
                new ol.layer.Tile({
                        title: 'Profit 2015',
                		visible: true,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2015/{z}/{x}/{y}.png'
                        })
                }),
                new ol.layer.Tile({
                        title: 'Profit 2014',
                		visible: false,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2014/{z}/{x}/{y}.png'
                        })
                }),
                new ol.layer.Tile({
                        title: 'Profit 2013',
                		visible: false,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2013/{z}/{x}/{y}.png'
                        })
                }),
                new ol.layer.Tile({
                        title: 'Profit 2012',
                		visible: false,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2012/{z}/{x}/{y}.png'
                        })
                }),
                new ol.layer.Tile({
                        title: 'Profit 2011',
						visible: false,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2011/{z}/{x}/{y}.png'
                        })
                })],
		view: new ol.View({
                        projection: 'EPSG:3857',
					center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
		
                })
		});
    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);
		
		
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
</style>
<div style="width:100%; height:100%" id="map">
<div id="legend"><img src="profit_legend.png" /></div>		
</div>

EOF;

$t->render('app.phtml');

?>