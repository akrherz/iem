<?php
include("../../config/settings.inc.php");
include("$rootpath/include/google_keys.php");

/* Pure IEM 2.0 App to do vtec stuff.  Shorter url please as well */
$v = isset($_GET["vtec"]) ? $_GET["vtec"] : "2008-O-NEW-KJAX-TO-W-0048";
$tokens = split("-", $v);
$year = $tokens[0];
$operation = $tokens[1];
$vstatus = $tokens[2];
$wfo4 = $tokens[3];
$wfo = substr($wfo4,1,3);
$phenomena = $tokens[4];
$significance = $tokens[5];
$eventid = intval( $tokens[6] );

$extjs = "ext-all.js";
if ($rootpath == "http://localhost/iem"){
  $extjs = "ext-all-debug.js";
}

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.0.0/resources/css/ext-all.css"/>
<link rel="stylesheet" type="text/css" href="../ext/ux/form/Spinner.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.0.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.0.0/ext-all.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="Ext.ux.GMapPanel.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="../ext/ux/menu/EditableItem.js"></script>
<script type="text/javascript" src="../ext/ux/grid/GridFilters.js"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/Filter.js"></script>
<script type="text/javascript" src="../ext/ux/form/Spinner.js"></script>
<script type="text/javascript" src="../ext/ux/form/SpinnerStrategy.js"></script>
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["vtec"] .'" type="text/javascript"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/StringFilter.js"></script>
<script>
Ext.namespace("cfg");
cfg.startYear = 2002;
cfg.header = "iem-header";
</script>
<script type="text/javascript" src="static.js?v=1.0.3"></script>';
$TITLE = "IEM Valid Time Extent Code (VTEC) App";
$NOCONTENT = 1;
$THISPAGE ="severe-vtec";
include("$rootpath/include/header.php");
?>

<div id="help">
 <h2>IEM VTEC Product Browser 2.0</h2>

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
</ul></p>
</div>
<div id="footer"></div>
<script>
Ext.onReady(function(){
  var tokens = window.location.href.split('#');
  cgiWfo = "<?php echo $wfo; ?>";
  cgiPhenomena = "<?php echo $phenomena; ?>";
  cgiSignificance = "<?php echo $significance; ?>";
  cgiEventId = "<?php echo $eventid; ?>";
  cgiYear = "<?php echo $year; ?>";
  if (tokens.length == 2){
    var subtokens = tokens[1].split("-");
    if (subtokens.length == 7){
      cgiWfo = subtokens[3].substr(1,3);
      cgiPhenomena = subtokens[4];
      cgiSignificance = subtokens[5];
      cgiEventId = subtokens[6];
      cgiYear = subtokens[0];
    }
  } 
  Ext.getCmp("wfoselector").setValue(cgiWfo);
  Ext.getCmp("phenomenaselector").setValue(cgiPhenomena);
  Ext.getCmp("significanceselector").setValue(cgiSignificance);
  Ext.getCmp("eventid").setValue(cgiEventId);
  Ext.getCmp("yearselector").setValue(cgiYear);
  Ext.getCmp('mainbutton').fireEvent('click', {});
});
</script>
</body></html>
