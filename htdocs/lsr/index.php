<?php
include("../../config/settings.inc.php");
include("$rootpath/include/google_keys.php");

$HEADEXTRA = '<script type="text/javascript" 
  src="http://extjs.cachefly.net/builds/ext-cdn-771.js"></script>
<link rel="stylesheet" type="text/css" 
   href="http://extjs.cachefly.net/ext-2.2.1/resources/css/ext-all.css" />
<link rel="stylesheet" type="text/css" 
  href="http://extjs.cachefly.net/ext-2.2.1/examples/shared/examples.css" />
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["vtec"] .'" type="text/javascript"></script>
<script src="http://openlayers.org/api/2.8/OpenLayers.js"></script>
<script type="text/javascript" src="GeoExt.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="MultiSelect.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="static.js"></script>';
$TITLE = "IEM Local Storm Report App";
$NOCONTENT = 1;
$THISPAGE ="severe-lsr";
include("$rootpath/include/header.php");
?>
<script>
Ext.onReady(function(){
});
</script>
</body></html>
