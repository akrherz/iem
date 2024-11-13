<?php
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";
// Maps app is not happy with non HTTPS
force_https();
// If CGI vtec parameter is set, we want to redirect to the new URL
if (isset($_GET["vtec"])){
  header("Location: /vtec/event/". xssafe($_GET["vtec"]));
  die();
}
require_once "../../include/myview.php";
$OL = "10.1.0";
$JQUERYUI = "1.13.2";
$t = new MyView();
$t->title = "Valid Time Event Code (VTEC) App";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" />
<link rel="stylesheet" href="/vendor/jquery-ui/{$JQUERYUI}/jquery-ui.min.css" />
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" href="/vtec/vtec_static.css" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/jquery-datatables/1.10.20/datatables.min.js"></script>
<script src="/vendor/jquery-ui/{$JQUERYUI}/jquery-ui.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script type="text/javascript" src="/vtec/vtec_static.js?20241113"></script>
<script type="text/javascript" src="/vtec/vtec_app.js?20241113"></script>
EOM;

$theform = <<<EOM
<form name="control" id="myform">

<p><strong>Find VTEC Product:</strong></p>

<div class="form-group">
<label for="wfo">Select Forecast Office</label>
<select name="wfo" id="wfo" class="form-control"></select>
</div>

<div class="form-group">
<label for="phenomena">Phenomena</label>
<select name="phenomena" id="phenomena" class="form-control"></select>
</div>

<div class="form-group">
<label for="significance">Significance</label>
<select name="significance" id="significance" class="form-control"></select>
</div>

<div class="form-group">
<button type="button" id="etn-prev" class="btn btn-default">
<i class="fa fa-arrow-left"></i></button>
<label for="etn">Event Number</label>
<button type="button" id="etn-next" class="btn btn-default">
<i class="fa fa-arrow-right"></i></button>
<input type="text" name="etn" id="etn" class="form-control" maxlength="4">
</div>

<div class="form-group">
<label for="year">Event Year</label>
<select name="year" id="year" class="form-control"></select>
</div>

<p>
<button type="button" id="myform-submit" class="btn btn-default">
<i class="fa fa-search"></i> Load Product</button>
</p>

</form>

EOM;

$helpdiv = <<<EOM
<div id="help">
 <h2>IEM VTEC Product Browser</h2>

<p>This application allows easy navigation of National Weather Service
issued products with Valid Time Event Coding (VTEC).</p>

<p><strong>13 Nov 2024 Update:</strong> The tool was updated to use non-hash
link style URLs.  A shim is in place to translate the old URLs to the new
ones, so nothing should be broken (famous last words). This was done to
allow the HTML5 History API to provide a better user experience.</p>

<p><strong>Tab Functionality:</strong>
<br /><i>Above this section, you will notice six selectable tabs. Click on 
the tab to show the information.</i>
<br /><ul>
 <li><b>Help:</b> This page!</li>
 <li><b>Event Info:</b> Details of the selected event.</li>
 <li><b>Text Data:</b> The raw text product for this event.</li>
 <li><b>Interactive Map:</b> An interactive map showing the event and RADAR.</li>
 <li><b>Storm Reports:</b> Local Storm Reports.</li>
 <li><b>List Events:</b> List all events of the given phenomena, significance, year, and issuing office.</li>
</ul>
</p>

<p><strong>Web Services Used:</strong>
<br />This application is fully driven by IEM <a href="/api/">web services</a>.
</p>

</div>
EOM;

$infodiv = <<<EOM

<p><strong><span id="vtec_label"></span></strong></p>

<div id="info_event_not_found" style="display: none;">
<p>Yikes! The event you requested was not found.  Please try another search.</p>
</div>

<div id="info_event_found" style="display: block;">
<button type="button" id="lsr_kml_button" class="btn btn-default"><i class="fa fa-search"></i> LSR KML Source</button>
<button type="button" id="warn_kml_button" class="btn btn-default"><i class="fa fa-search"></i> Warning KML Source</button>
<button type="button" id="ci_kml_button" class="btn btn-default"><i class="fa fa-search"></i> County Intersection KML Source</button>
<button type="button" id="gr_button" class="btn btn-default"><i class="fa fa-search"></i> Gibson Ridge Placefile</button>

<h3>Listing of Counties/Parishes/Zones Included in Product</h3>

<div class="pull-right">
    <button class="btn btn-default"
    onclick="selectElementContents('ugctable');">
    <i class="fa fa-clipboard"></i> Copy Table to Clipboard
    </button>
</div>


<table id="ugctable" style="width: 100%">
<thead>
<tr>
 <th>UGC</th>
 <th>Name</th>
 <th>Status</th>
 <th>Issuance</th>
 <th>Issue</th>
 <th>Initial Expire</th>
 <th>Expire</th>
</tr>
</thead>
<tbody>

</tbody>
</table>


<h3>RADAR Composite at Issuance Time</h3>

<div id="radarmap"></div>

<h3>Storm Based Warning History</h3>

<div id="sbwhistory"></div>

</div><!-- ./info_event_found -->

EOM;

$eventsdiv = <<<EOM

<p>This table lists other events issued by the selected office for the
selected year.  Click on the row to select that event.</p> 

<div class="pull-right">
    <button class="btn btn-default"
    onclick="selectElementContents('eventtable');">
    <i class="fa fa-clipboard"></i> Copy Events to Clipboard
    </button>
</div>

<table id="eventtable" style="width:100%">
<thead>
<tr>
 <th>ID</th>
 <th>Product Issued</th>
 <th>VTEC Issued</th>
 <th>Initial Expire</th>
 <th>VTEC Expire</th>
 <th>Area km**2</th>
 <th>Locations</th>
 <th>Signature</th>
</tr>
</thead>
<tbody>

</tbody>
</table>

EOM;

$lsrsdiv = <<<EOM

<p><h3>All Storm Reports within Event Political Coverage</h3></p>

<div class="pull-right">
    <button class="btn btn-default"
    onclick="selectElementContents('lsrtable');">
    <i class="fa fa-clipboard"></i> Copy LSRs to Clipboard
    </button>
</div>


<table id="lsrtable" style="width: 100%">
<thead>
<tr>
 <th></th>
 <th>Time</th>
 <th>Event</th>
 <th>Magnitude</th>
 <th>City</th>
 <th>County</th>
</tr>
</thead>
<tbody>

</tbody>
</table>

<p><h3>Storm Reports within Product Polygon</h3></p>

<div class="pull-right">
    <button class="btn btn-default"
    onclick="selectElementContents('sbwlsrtable');">
    <i class="fa fa-clipboard"></i> Copy LSRs to Clipboard
    </button>
</div>


<table id="sbwlsrtable" style="width: 100%">
<thead>
<tr>
 <th></th>
 <th>Time</th>
 <th>Event</th>
 <th>Magnitude</th>
 <th>City</th>
 <th>County</th>
</tr>
</thead>
<tbody>

</tbody>
</table>


EOM;

$mapdiv = <<<EOM

<div class="row">
  <div class="col-md-3">
    <div class="form-group">
        <label for="radarsource">RADAR Source</label>
        <select id="radarsource" class="form-control"></select>
    </div>
  </div>
  <div class="col-md-3">
    <div class="form-group">
        <label for="radarproduct">RADAR Product</label>
        <select id="radarproduct" class="form-control"></select>
    </div>
  </div>
  <div class="col-md-3">
    <div class="form-group">
        <label for="radaropacity">RADAR Opacity</label>
        <div id="radaropacity" class="form-control"></div>
    </div>
  </div>
  <div class="col-md-3">
    <div class="form-group">
        <label for="timeslider">Time <span id="radartime"></span></label>
        <div id="timeslider" class="form-control"></div>
    </div>
  </div>
</div>

<div id="map"></div>
<div id="popup" class="ol-popup"></div>
EOM;

$textdiv = <<<EOM

<button type="button" id="toolbar-print" class="btn btn-default">
<i class="fa fa-print"></i> Send Text to Printer</button>

<ul class="nav nav-tabs" id="text_tabs">
    <li class="active"><a href="#t0" data-toggle="tab">Issuance</a></li>
</ul>
<div class="tab-content clearfix">
    <div class="tab-pane active" id="t0">Text Product Issuance</div>
</div>
EOM;

$t->content = <<<EOF

<div class="clearfix">&nbsp;</div>

<div class="row">
  <div class="col-md-3 well">
    {$theform}
  </div><!-- ./col-md-3 -->
  <div class="col-md-9">

<div class="panel with-nav-tabs panel-default" id="thetabs">
    <div class="panel-heading">
      <ul class="nav nav-tabs" id="thetabs_tabs">
         <li class="active"><a href="#help" data-toggle="tab">Help</a></li>
         <li><a href="#info" data-toggle="tab">Event Info</a></li>
         <li><a href="#textdata" data-toggle="tab">Text Data</a></li>
         <li><a href="#themap" data-toggle="tab">Interactive Map</a></li>
         <li><a href="#stormreports" data-toggle="tab">Storm Reports</a></li>
         <li><a href="#listevents" data-toggle="tab">List Events</a></li>
      </ul>
    </div><!-- ./panel-heading -->
    <div class="panel-body">
     <div class="tab-content clearfix">

       <div class="tab-pane active" id="help">{$helpdiv}</div>
       <div class="tab-pane" id="info">
{$infodiv}
       </div><!-- ./info -->
       <div class="tab-pane" id="textdata">{$textdiv}</div>
       <div class="tab-pane" id="themap">{$mapdiv}</div>
       <div class="tab-pane" id="stormreports">{$lsrsdiv}</div>
       <div class="tab-pane" id="listevents">{$eventsdiv}</div>
    </div><!-- ./tab-content -->
    </div><!-- ./panel-body -->
  </div><!-- ./col-md-9 -->
</div><!-- ./row -->

EOF;
$t->render('full.phtml');
