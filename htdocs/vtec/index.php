<?php
require_once "../../config/settings.inc.php";
require_once "../../include/Mobile_Detect.php";

// Mobile business logic
$detect = new Mobile_Detect;
if ($detect->isMobile()){
  echo <<<EOF
<html>
<head>
<script>
  var tokens = window.location.href.split('#');
  if (tokens.length == 2){
    window.location = 'mobile.php?vtec='+ tokens[1];
  } else {
    window.location = 'mobile.php?vtec=2008-O-NEW-KJAX-TO-W-0048';
  }
  </script>
</head>
<body></body>
</html>
EOF;
  exit;
}
require_once "../../include/myview.php";
$t = new MyView();
$t->thispage = "severe-vtec";

/* Pure IEM 2.0 App to do vtec stuff.  Shorter url please as well */
$v = isset($_GET["vtec"]) ? $_GET["vtec"] : "2012-O-NEW-KBMX-TO-W-0001";
$tokens = preg_split('/-/', $v);
$year = $tokens[0];
$operation = $tokens[1];
$vstatus = $tokens[2];
$wfo4 = $tokens[3];
$wfo = substr($wfo4,1,3);
$phenomena = $tokens[4];
$significance = $tokens[5];
$eventid = intval( $tokens[6] );

$headextra = <<<EOF
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/3.4.1.1/resources/css/ext-all.css"/>
<link rel="stylesheet" type="text/css" href="/ext/ux/form/Spinner.css"/>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/3.4.1.1//adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/3.4.1.1/ext-all.js"></script>
<script src="OpenLayers_GeoExt.js"></script>
EOF;

if (isset($_REQUEST["devel"])){
    $headextra .= '<script type="text/javascript" src="js/wfos.js"></script>
<script type="text/javascript" src="js/RowExpander.js"></script>
<script type="text/javascript" src="js/Printer-all.js"></script>
<script type="text/javascript" src="/ext/ux/menu/EditableItem.js"></script>
<script type="text/javascript" src="/ext/ux/grid/GridFilters.js"></script>
<script type="text/javascript" src="/ext/ux/grid/filter/Filter.js"></script>
<script type="text/javascript" src="/ext/ux/form/Spinner.js"></script>
<script type="text/javascript" src="/ext/ux/form/SpinnerStrategy.js"></script>
<script type="text/javascript" src="/ext/ux/grid/filter/StringFilter.js"></script>
<script type="text/javascript" src="js/overrides.js"></script>
<script type="text/javascript" src="js/RadarPanel.js"></script>
<script type="text/javascript" src="js/LSRFeatureStore.js"></script>
<script type="text/javascript" src="js/SBWFeatureStore.js"></script>
<script type="text/javascript" src="js/SBWIntersectionFeatureStore.js"></script>
<script type="text/javascript" src="js/Ext.ux.SliderTip.js"></script>
<script type="text/javascript" src="js/static.js"></script>';
} else {
	$headextra .= '<script src="app.js?v=11"></script>';
}

$headextra .= <<<EOF
<script>
Ext.namespace("cfg");
cfg.startYear = 1986;
cfg.header = "iem-header";
cfg.footer = "iem-footer";
</script>
EOF;

$t->headextra = $headextra;
$t->title = "Valid Time Extent Code (VTEC) App";
$t->content = <<<EOF
<div id="iem-header">
<a href="/">IEM Homepage</a> &gt; <a href="/current/severe.phtml">Severe Weather Mainpage</a>
</div>
<div id="iem-footer">
</div>
<div id="help">
 <h2>IEM VTEC Product Browser 3.0</h2>

 <p>This application allows easy navigation of National Weather Service
issued products with Valid Time Extent Coding (VTEC).</p>

<p style="margin-top: 10px;"><b>Tab Functionality:</b>
<br /><i>Above this section, you will notice 9 selectable tabs. Click on 
the tab to show the information.</i>
<br /><ul>
 <li><b>Help:</b>  This page!</li>
 <li><b>RADAR Map:</b>  Simple map displaying the product geography.</li>
 <li><b>Text Data:</b>  The raw text based products issued by the National Weather Service.  Any follow-up products are included as well.</li>
 <li><b>Google Map:</b>  Product and Storm Reports over Google Maps.</li>
 <li><b>SBW History:</b>  Displays changes in storm based warnings.</li>
 <li><b>Storm Reports within SBW:</b>  Storm Reports inside Storm Based Warning.</li>
 <li><b>All Storm Reports:</b>  Any Storm Reports during the time of the product for the issuing office.</li>
 <li><b>Geography Included:</b>  Counties/Zones affected by this product.</li>
 <li><b>List Events:</b>  List all events of the given phenomena, significance, year, and issuing office.</li>
</ul>
</div>
<div id="boilerplate"></div>
<div id="footer"></div>
<script>
Ext.ns("App");
Ext.onReady(function(){
  var tokens = window.location.href.split('#');
  cgiWfo = "{$wfo}";
  cgiPhenomena = "{$phenomena}";
  cgiSignificance = "{$significance}";
  cgiEventId = "{$eventid}";
  cgiYear = "{$year}";
  if (tokens.length == 2){
    var subtokens = tokens[1].split("/");
    var vtectokens = subtokens[0].split("-");
    if (vtectokens.length == 7){
      cgiWfo = vtectokens[3].substr(1,3);
      cgiPhenomena = vtectokens[4];
      cgiSignificance = vtectokens[5];
      cgiEventId = vtectokens[6].substr(0,4);
      cgiYear = vtectokens[0];
    }
    if (subtokens.length > 1){
		var radartokens = subtokens[1].split("-");
		if (radartokens.length == 3){
			
			App.initRadar = radartokens[0];
			App.initRadarProduct = radartokens[1];
			try{
				App.initRadarTime = Date.parseDate(radartokens[2],'YmdHi');
			} catch(err) {}
		}
    }
  } 
  Ext.getCmp("wfoselector").setValue(cgiWfo);
  Ext.getCmp("phenomenaselector").setValue(cgiPhenomena);
  Ext.getCmp("significanceselector").setValue(cgiSignificance);
  Ext.getCmp("eventid").setValue(cgiEventId);
  Ext.getCmp("yearselector").setValue(cgiYear);
  Ext.getCmp("mainPanel").activate(3);
});
</script>
EOF;
$t->render('app.phtml');
?>
