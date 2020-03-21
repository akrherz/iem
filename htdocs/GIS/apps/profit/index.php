<?php 
require_once "../../../../config/settings.inc.php";

require_once "../../../../include/myview.php";

$OL = "6.2.1";
$t = new MyView();
$t->title = "Profitability Map";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script>
var map;
var player;
$(document).ready(function(){
	player = new ol.layer.Tile({
                        title: 'Profitability',
						visible: true,
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/profit2010/{z}/{x}/{y}.png'
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
	$("#disclaimer_btn").click(function(){
		$('#disclaimer').dialog({width: '50%', height: 400});	
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
		a {
		color: #00f !important;
		text-decoration: underline !important;
		}
</style>
<div style="width:100%; height:100%" id="map">
<div id="yearselect">
  <input type="radio" id="y2010" name="whichyear" value="2010" checked="checked"><label for="y2010">2010</label>
  <input type="radio" id="y2011" name="whichyear" value="2011"><label for="y2011">2011</label>
  <input type="radio" id="y2012" name="whichyear" value="2012"><label for="y2012">2012</label>
  <input type="radio" id="y2013" name="whichyear" value="2013"><label for="y2013">2013</label>
  <input type="radio" id="y2015" name="whichyear" value="2015"><label for="y2015">2015</label>
</div>
		
<div id="legend"><img src="profit_legend.png" />
<br /><button class="btn btn-default" id="disclaimer_btn" type="button" role="button"><i class="fa fa-info"></i> View Disclaimer</button>
</div>

<div id="disclaimer" style="display: none; overflow: auto;" title="Disclaimer">
<p>
This map shows estimates of profitability of fields in corn or
soybean. This map is meant to provide insight into alternative land
management to improve farm profitability using publically available
(and funded) data, thus allowing access without purchase of a private
farm data management plan. While useful for insight into relative
performance of areas within fields, and representative of Iowa farm
management, this map does not contain individual economic or
management data, and actual profitability will depend on actual
expenses, revenue and management. We present a snapshot of the
current possibilities with the available data and hope to improve
this map in the future to allow user-defined values for
individualized results. Local variations of yields, management and
marketing practices, land tenure, and inaccuracy of the underlying
spatial data result in deviations from the estimates presented here.</p>

<p>For a complete
description of the underlying data and methods, please refer to the
research article “Subfield profitability analysis reveals an
economic case for cropland diversification,” that can be freely
accessed <a href="http://iopscience.iop.org/article/10.1088/1748-9326/11/1/014009/meta;jsessionid=0059946EA9A46A2380CB698ABA6BAA8C.c4.iopscience.cld.iop.org">online</a>.</p>

<p>The analysis was
performed for fields that were planted in corn or soybeans according
to the <a href="http://nassgeodata.gmu.edu/CropScape/">cropland data
layer</a> (CDL) for 2010-2013. The 2013 CDL was used for 2015.
Patches of similar profitability are defined by <a href="http://websoilsurvey.sc.egov.usda.gov/">soil
survey</a> (SSURGO) and <a href="http://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-products/common-land-unit-clu/index">common
land unit</a> (CLU, 2008) delineations. Profitability was calculated
by deducting cash rent and crop production cost estimates from the
crop revenue (crop yield x grain price). Potential yields were taken
from the <a href="http://www.extension.iastate.edu/soils/ispaid">Iowa
soil properties and interpretations database (ISPAID)</a> and
adjusted to <a href="http://quickstats.nass.usda.gov">average county
yields</a> (NASS, 2010-2013) or to <a href="http://webapp.rma.usda.gov/apps/actuarialinformationbrowser/">trend
county yields</a> (USDA RMA, 2015). Grain prices are the average
monthly prices of each marketing year, and the forecast for 2015 from
the <a href="http://usda.mannlib.cornell.edu/MannUsda/viewDocumentInfo.do?documentID=1194">USDA
WASDE report</a> of May 2016. Cash rents are taken from <a href="https://www.extension.iastate.edu/agdm/wholefarm/html/c2-10.html">county
surveys</a> (ISU extension, 2010-2013, 2015), adjusted to corn
suitability rating (CSR). Crop production costs were taken from the
<a href="http://www.extension.iastate.edu/agdm/crops/html/a1-20.html">ISU
Ag Decision Maker cost estimates</a>.</p>
		
</div><!-- ./disclaimer -->
</div>

EOF;

$t->render('app.phtml');

?>