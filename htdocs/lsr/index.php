<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$OL = "7.2.2";
$DT = "1.11.1";
$S2 = "4.1.0rc0";

$t = new MyView();
$t->jsextra = <<<EOF
<!-- need to load before datatables -->
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src="/vendor/jquery-datatables/{$DT}/datatables.min.js"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script
 src="/vendor/datetimepicker/2.5.20/jquery.datetimepicker.full.min.js">
</script>
<script src="/vendor/select2/{$S2}/select2.min.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>

<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="static.js?v=6"></script>
<script>
$(document).ready(function(){
    initUI(); // static.js
    parse_href();
    window.setInterval(cronMinute, 60000);
});
</script>
EOF;
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/jquery-datatables/{$DT}/datatables.min.css" />
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link rel="stylesheet" type="text/css"
href="/vendor/datetimepicker/2.5.20/jquery.datetimepicker.min.css" />
<link rel="stylesheet" type="text/css" href="/vendor/select2/{$S2}/select2.min.css"/ >
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link type="text/css" href="static.css" rel="stylesheet" />
EOM;
$t->title = "Local Storm Report App";
$tab1a = <<<EOM
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
EOM;
$tab2a = <<<EOM
<br />
<p>
<strong>Tools:</strong> &nbsp;
<button id="lsrexcel" class="btn btn-primary" role="button"><i class="fa fa-download"></i> Excel</button>
<button id="lsrkml" class="btn btn-primary" role="button"><i class="fa fa-download"></i> KML</button>
<button id="lsrshapefile" class="btn btn-primary" role="button"><i class="fa fa-download"></i> Shapefile</button>
<select name="lt" id="lsrtypefilter" class="form-control"></select>
</p>

<br />
<table id="lsrtable">
<thead>
<tr>
  <td></td>
  <td></td>
  <th>WFO</th>
  <th>Report Time</th>
  <th>County</th>
  <th>Location</th>
  <th>State</th>
  <th>Event Type</th>
  <th>Magnitude</th>
</tr>
</thead>
</table>

EOM;
$tab3a = <<<EOM
<br />
<p>
<strong>Tools:</strong> &nbsp;
<button id="warnshapefile" class="btn btn-primary" role="button">Get Shapefile</button>
<button id="warnexcel" class="btn btn-primary" role="button">Get Excel</button>
<button id="sbwshapefile" class="btn btn-primary" role="button">Get SBW Shapefile</button>
<select name="lt" id="sbwtypefilter" class="form-control"></select>
</p>


<table id="sbwtable">
<thead>
<tr>
  <td></td><td></td>
  <th>WFO</th>
  <th>Phenomena</th>
  <th>Significance</th>
  <th>Event ID</th>
  <th>Issues</th>
  <th>Expires</th>
</tr>
</thead>
</table>
EOM;
$theform = <<<EOM
<div class="row">
<div class="col-md-6">
<div class="form-group">
<label for="wfo">Select WFO: (default ALL)</label>
<select name="wfo" id="wfo" class="form-control" multiple="multiple"></select>
<br /><input type="checkbox" id="realtime" name="rt">
  <label for="realtime"> Auto Refresh/Realtime</label>
</div>
</div><!-- ./col-md-6 -->
<div class="col-md-6">

<div class="form-group">
<label for="sts">Start Time</label>
<input id="sts" name="sts" class="iemdtp">
</div>

<div class="form-group">
<label for="ets">End Time</label>
<input id="ets" name="ets" class="iemdtp">
</div>
</div><!-- ./col-md-6 -->
</div><!-- ./row -->

<div class="row">
<div class="col-md-10">

<div class="form-group">
<label for="timeslider">RADAR Time: <span id="radartime"></span></label>
<div id="timeslider" class="form-control">
<div id="custom-handle" class="ui-slider-handle"></div>
</div>
</div>

</div>
<div class="col-md-2">

<button id="load" type="button" class="btn btn-primary">Load</button>

</div><!-- ./col-md-2 -->
</div><!-- ./row -->

EOM;
$t->content = <<<EOM

<div class="row">
  <div class="col-md-5" id="leftside">
    {$theform}
    <div id="map"></div>
  </div><!-- ./col-md-5 -->
  <div class="col-md-7" id="rightside">

  <div class="tab", role="tabpanel">
    <ul class="nav nav-tabs" role="tablist">
        <li class="active"><a href="#1a" data-toggle="tab">Help</a></li>
        <li><a id="lsrtab" href="#2a" data-toggle="tab">Local Storm Reports</a></li>
        <li><a href="#3a" data-toggle="tab">Storm Based Warnings</a></li>
    </ul>

    <div class="tab-content tabs clearfix">
        <div role="tabpanel" class="tab-pane active" id="1a">
            {$tab1a}
        </div>
        <div role="tabpanel" class="tab-pane" id="2a">
            {$tab2a}
        </div>
        <div role="tabpanel" class="tab-pane" id="3a">
            {$tab3a}
        </div>

    </div>
  </div><!-- ./tabs -->
  </div><!-- ./col-md-7 -->
</div><!-- ./row -->


EOM;
$t->render('full.phtml');
