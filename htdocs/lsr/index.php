<?php
include("../../config/settings.inc.php");
include("$rootpath/include/google_keys.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.1.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.1.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.1.0/ext-all.js"></script>
<link rel="stylesheet" type="text/css" 
  href="superboxselect.css" />
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["any"] .'" type="text/javascript"></script>
<script src="http://openlayers.org/api/2.8/OpenLayers.js"></script>
<script type="text/javascript" src="GeoExt.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="SuperBoxSelect.js"></script>
<script type="text/javascript" src="static.js"></script>
';
$TITLE = "IEM Local Storm Report App";
$NOCONTENT = 1;
$THISPAGE ="severe-lsr";
include("$rootpath/include/header.php");
?>
<script>
Ext.onReady(function(){
  var tokens = window.location.href.split('#');
  if (tokens.length == 2){
    var tokens2 = tokens[1].split("/");
    if (tokens2.length == 3){
      Ext.getCmp("wfoselector").setValue( tokens2[0].split(",") );
      utc_start  = Date.parseDate(tokens2[1], 'YmdHi');
      Ext.getCmp("datepicker1").setValue( utc_start.fromUTC() );
      Ext.getCmp("timepicker1").setValue( utc_start.fromUTC() );
      utc_end    = Date.parseDate(tokens2[2], 'YmdHi');
      Ext.getCmp("datepicker2").setValue( utc_end.fromUTC() );
      Ext.getCmp("timepicker2").setValue( utc_end.fromUTC() );
      Ext.getCmp('refresh').fireEvent('click', {});
    }
  }
});
</script>
<div id="help">
<h3>Help Me!</h3>
<h3>Help Me!</h3>
<h3>Help Me!</h3>
<h3>Help Me!</h3>
<h3>Help Me!</h3>
<br />
<br />
<br />
<br />
a

</div>
</body></html>
