<?php
include("../../config/settings.inc.php");
include("$rootpath/include/google_keys.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.2.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.1/ext-all.js"></script>
<link rel="stylesheet" type="text/css" href="superboxselect.css" />
<script src="http://maps.google.com/maps?file=api&amp;v=2.x&amp;key='. $GOOGLEKEYS[$rooturl]["any"] .'" type="text/javascript"></script>
<script src="http://www.openlayers.org/api/2.9/OpenLayers.js"></script>
<script type="text/javascript" src="GeoExt.js"></script>
<script type="text/javascript" src="RowExpander.js"></script>
<script type="text/javascript" src="Printer-all.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="SuperBoxSelect.js"></script>
<script type="text/javascript" src="Exporter-all.js"></script>
<script>
Ext.namespace("cfg");
cfg.header = "iem-header";
</script>
<script type="text/javascript" src="static.js?v=10"></script>
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
    if (tokens2.length == 2){
      Ext.getCmp("wfoselector").setValue( tokens2[0].split(",") );
      d = (new Date()).add(Date.SECOND, parseInt(tokens2[1]) );
      Ext.getCmp("datepicker1").setValue( d );
      Ext.getCmp("timepicker1").setValue( d );
      Ext.getCmp("datepicker2").setValue( new Date() );
      Ext.getCmp("timepicker2").setValue( new Date() );
      Ext.getCmp('refresh').fireEvent('click', {});
      Ext.getCmp('rtcheckbox').setValue(true);
    }
    if (tokens2.length > 2){
      Ext.getCmp("wfoselector").setValue( tokens2[0].split(",") );
      utc_start  = Date.parseDate(tokens2[1], 'YmdHi');
      Ext.getCmp("datepicker1").setValue( utc_start.fromUTC() );
      Ext.getCmp("timepicker1").setValue( utc_start.fromUTC() );
      utc_end    = Date.parseDate(tokens2[2], 'YmdHi');
      Ext.getCmp("datepicker2").setValue( utc_end.fromUTC() );
      Ext.getCmp("timepicker2").setValue( utc_end.fromUTC() );
      Ext.getCmp('refresh').fireEvent('click', {});
    }
    if (tokens2.length == 4){ /* Extra options were specified */
      Ext.getCmp('refresh').fireEvent('boilerup', tokens2[3]);
    }
  }
});
</script>
<div id="help" style="padding:5px;">
<h3>Local Storm Report App Help</h3>
<br />
<p>This application allows the quick viewing of National Weather Service (NWS)
issued Local Storm Reports (LSR).  These LSRs are issued by local NWS forecast
offices for their area of responsibility.</p>
<br />
<p>To use this application, select the NWS forecast office(s) of choice and
then a time duration you are interested in.  Times presented on this 
application are in the timezone of your local computer.</p>
<br />
<p>After selecting a time period and office(s), this application will 
automatically generate a listing of any available LSR reports and also
generate a listing of Storm Based Warnings (SBW)s valid for some portion
of the period of interest.  You can switch between these data listings
by click on the tabs found just above this text.</p>
<br />
<p>The map interface on the right hand side visually presents these LSRs
and SBWSs.  Clicking on the icon or polygon, highlights the corresponding
data in the two tables.</p>
<br />
<p>You also have the ability to overlay NEXRAD base reflectivity information
for any 5 minute interval during the time period of your choice.</p>
<br />
<h3>Linking to this Application</h3>
<p>This application uses stable URLs allowing you to bookmark and easily
generate links to it.  Currently, there are two calling modes:</p>
<br />
<p><i>/lsr/#WFO,WFO2/YYYYMMDDHHII/YYYYMMDDHHII</i> : where you can list
  none or any number of Weather Forecast Office IDs.  Then there are two
  timestamps in UTC time zone (beginning and end time).</p>
<br />
<p><i>/lsr/#WFO,WFO2/-SECONDS</i> : again, you can list none or multiple
  WFO IDs.  You can then specify a number of seconds from now into the
  past.  For example, <i>/lsr/#LWX/-86400</i> would produce LSRs from
  LWX for the past day (86400 seconds).</p>
<br />


</div>
</body></html>
