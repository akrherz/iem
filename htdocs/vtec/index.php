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

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="../ext/resources/css/ext-all.css"/>
<script type="text/javascript" src="../ext/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="../ext/ext-all.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="Ext.ux.GMapPanel.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="../ext/ux/menu/EditableItem.js"></script>
<script type="text/javascript" src="../ext/ux/grid/GridFilters.js"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/Filter.js"></script>
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["vtec"] .'" type="text/javascript"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/StringFilter.js"></script>
<script type="text/javascript" src="static.js?v=1.0.1"></script>';
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
  Ext.getCmp("wfoselector").setValue("<?php echo $wfo; ?>");
  Ext.getCmp("phenomenaselector").setValue("<?php echo $phenomena; ?>");
  Ext.getCmp("significanceselector").setValue("<?php echo $significance; ?>");
  Ext.getCmp("eventid").setValue("<?php echo $eventid; ?>");
  Ext.getCmp("yearselector").setValue("<?php echo $year; ?>");

  Ext.getCmp('mainbutton').fireEvent('click', {});
});
</script>
</body></html>
