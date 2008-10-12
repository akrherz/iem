<?php
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

?>

<html>
<head>
<link rel="stylesheet" type="text/css" href="../ext/resources/css/ext-all.css"/>
<script type="text/javascript" src="../ext/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="../ext/ext-all.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key=ABQIAAAAJDLv3q8BFBryRorw-851MRT2yXp_ZAY8_ufC3CFXhHIE1NvwkxTyuslsNlFqyphYqv1PCUD8WrZA2A" type="text/javascript"></script>
<script type="text/javascript" src="Ext.ux.GMapPanel.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="../ext/ux/menu/EditableItem.js"></script>
<script type="text/javascript" src="../ext/ux/grid/GridFilters.js"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/Filter.js"></script>
<script type="text/javascript" src="../ext/ux/grid/filter/StringFilter.js"></script>
<script type="text/javascript" src="static.js"></script>
</head>
<body>


<div id="header"></div>
<div id="help">
 <h3>Help me! <?php echo $v; ?></h3>
</div>
<div id="footer"></div>
<script>
Ext.onReady(function(){
  Ext.getCmp("wfoselector").setValue("<?php echo $wfo; ?>");
  Ext.getCmp("phenomenaselector").setValue("<?php echo $phenomena; ?>");
  Ext.getCmp("significanceselector").setValue("<?php echo $significance; ?>");
  Ext.getCmp("eventid").setValue("<?php echo $eventid; ?>");
  Ext.getCmp("yearselector").setValue("<?php echo $year; ?>");
});
</script>
</body></html>
