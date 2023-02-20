<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 120);
$OL = "7.2.2";
$JQUERYUI = "1.13.2";

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$t = new MyView();
$t->title = "Tornado + Flash Flood Emergencies Listing";
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
<link rel="stylesheet" href="/vendor/jquery-ui/{$JQUERYUI}/jquery-ui.min.css" />
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script src="/vendor/jquery-ui/{$JQUERYUI}/jquery-ui.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="emergencies.js"></script>
EOM;


$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">Tornado + Flash Flood Emergencies</li>
</ol>
<h3>NWS Tornado + Flash Flood Emergencies</h3>

<div class="alert alert-info">This page presents the current
<strong>unofficial</strong> IEM
accounting of Tornado and Flash Flood Emergencies issued by the NWS.  If you find
any discrepancies, please <a href="/info/contacts.php">let us know</a>!
 You may wonder how events prior to the implementation
of VTEC have eventids.  These were retroactively generated and assigned by the IEM.
</div>

<p>Link to <a href="https://en.wikipedia.org/wiki/List_of_United_States_tornado_emergencies">Wikipedia List of United States tornado emergencies</a>.</p>

<p>There is a <a href="/api/1/docs#/vtec/service_nws_emergencies__fmt__get">IEM webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/api/1/nws/emergencies.geojson</code></p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/vtec/pds.php">PDS Warnings</a>
&nbsp;
<a class="btn btn-primary" href="/nws/pds_watches.php">SPC PDS Watches</a>
&nbsp;
</p>

<style>
#map {
    width: 100%;
    height: 400px;
}
.popover {
    min-width: 400px;
}
</style>
<div id="map"></div>
<div id="popup" class="ol-popup"></div>

<p><button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead><tr><th>Year</th><th>WFO</th><th>State(s)</th><th>Event ID</th>
<th>Event</th><th>Issue</th><th>Expire</th></tr>
</thead>
<tbody></tbody>
</table>
</div>

EOF;
$t->render("full.phtml");
