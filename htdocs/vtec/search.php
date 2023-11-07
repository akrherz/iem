<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 154);
require_once "../../include/mlib.php";
force_https();
require_once "../../include/myview.php";
require_once "../../include/iemprop.php";
$gmapskey = get_iemprop("google.maps.key");
$t = new MyView();

$t->jsextra = <<<EOF
<script type="text/javascript" src="/js/mapping.js"></script>
<script src="/vendor/jquery-datatables/1.10.20/datatables.min.js"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src="/vendor/select2/4.1.0rc0/select2.min.js"></script>
<script type="text/javascript" src="wfos.js"></script>
<script type="text/javascript" src="search.js?v=6"></script>
<script src="https://maps.googleapis.com/maps/api/js?key={$gmapskey}&callback=_load" type="text/javascript"></script>
EOF;
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" />
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.1.0rc0/select2.min.css"/ >
<style>
  .map {
    width: 100%;
    height: 400px;
    float: left;
  }
</style>
EOF;
$t->title = "NWS Warning Search by Point or County/Zone";

$t->content = <<<EOF
<p>This application allows you to search for National Weather Service Watch,
Warning, and Advisories.  There are currently two options:
<ul>
    <li><a href="#bypoint">1. Search for Storm Based Warnings by Point</a></li>
    <li><a href="#byugc">2. Search of Watch/Warning/Advisories by County/Zone or by Point</a></li>
    <li><a href="#list">3. List Watch/Warning/Advisories by State/WFO by Year</a></li>
</ul>

<h3><a name="bypoint">1.</a> Search for Storm Based Warnings by Point</h3>

<br />The official warned area for some products the NWS issues is a polygon.
This section allows you to specify a point on the map below by dragging the 
marker to where you are interested in.  Once you stop dragging the marker, the
grid will update and provide a listing of storm based warnings found.  
<br clear="all" />
<div class="row">
    <div class="col-md-4">
        <p><strong>Either enter coordinates manually:</strong><br />
        <i>Latitude (deg N):</i> <input size="8" id="lat" value="41.53"><br />
        <i>Longitude (deg E):</i> <input size="8" id="lon" value="-93.653">
        <br /><label for="sdate1">Start Date:
            <input name="sdate1" type="text" id="sdate1"></label>
            <br /><label for="edate1">End Date:
            <input name="edate1" type="text" id="edate1"></label>
    
        <button type="button" class="btn btn-default" id="manualpt">Update</button>
        </p>
        <p><strong>Or drag marker to select coordinate:</strong><br />
        <div id="map" class="map"></div>
    </div>
    <div class="col-md-8">
    <h4 id="table1title"></h4>
    <button type="button" data-table="1" data-opt="excel" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to Excel...</button>
    <button type="button" data-table="1" data-opt="csv" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to CSV...</button>

    <table id="table1" data-order='[[ 3, "desc" ]]'>
    <thead>
    <tr><th>Event</th><th>Phenomena</th><th>Significance</th><th>Issued</th>
    <th>Expired</th><th>Issue Hail Tag</th><th>Issue Wind Tag</th>
    <th>Issue Tornado Tag</th><th>Issue Damage Tag</th></tr></thead>
    </table>
    </div>
</div>

<br clear="all" />
<h3><a name="byugc">2.</a> Search for NWS Watch/Warning/Advisories Products by County/Zone or by Point</h3>
<br />
<p>The NWS issues watch, warnings, and advisories (WWA) for counties/parishes.  For 
some products (like winter warnings), they issue for forecast zones.  
 In many parts of the country, these zones are exactly the 
 same as the counties/parishes.  When you get into regions with topography, 
 then zones will start to differ to the local counties.</p>

<p>This application allows you to search the IEM's archive of NWS WWA products.  
 Our archive is not complete, but there are no known holes since 12 November 2005. 
 This archive is of those products that contain VTEC codes, which are nearly all 
 WWAs that the NWS issues for. There are Severe Thunderstorm, Tornado, and 
 Flash Flood Warnings included in this archive for dates prior to 2005.  These  
 were retroactively assigned VTEC event identifiers by the IEM based on some
 hopefully intelligent logic.</p>
<br />
<div class="alert alert-warning">Please note: NWS forecast offices have 
changed over the years, this application may incorrectly label old warnings as coming from
an office that did not exist at the time.
        
    <br /><strong>Also note:</strong> This particular search interface will return
        <strong>false-positives</strong> for some warnings that are now fully polygon/storm based. The IEM
        database tracks the UGC areas associated with the storm based warnings. So querying
        by UGC (even if you query by point), will return some warnings that were not actually
        active for that point, but were technically active for that UGC of which the point
        falls inside of. Please use the above search for these types of warnings!
        </div>
<br />

<form id="form2">
<div class="row">
    <div class="col-md-4">
        <label for="state">Select State:
        <select name="state" style="width: 100%" id="state"></select></label>
        <br /><label for="ugc">Select County/Zone:
        <select name="ugc" style="width: 100%"></select></label>
        <br /><label for="sdate">Start Date:
        <input name="sdate" type="text"></label>
        <br /><label for="edate">End Date:
        <input name="edate" type="text"></label>
        
        <p><strong>You can otherwise search by lat/lon point. The start and
        end date set above are used with this option as well:</strong><br />
        <i>Latitude (deg N):</i> <input size="8" id="lat2" value="41.53"><br />
        <i>Longitude (deg E):</i> <input size="8" id="lon2" value="-93.653">
        <button type="button" class="btn btn-default" id="manualpt2">Update</button>
        </p>
        <p><strong>Or drag marker to select coordinate:</strong><br />
        <div id="map2" class="map"></div>
    </div>
    <div class="col-md-8">
    <h4 id="table2title"></h4>
    <button type="button" data-table="2" data-opt="excel" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to Excel...</button>
    <button type="button" data-table="2" data-opt="csv" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to CSV...</button>

    <table id="table2" data-order='[[ 3, "desc" ]]'>
    <thead>
    <tr><th>Event</th><th>Phenomena</th><th>Significance</th><th>Issued</th>
    <th>Expired</th></tr></thead>
    </table>
    </div>
</div><!-- ./row -->
</form><!-- ./form2 -->

<br clear="all" />
<h3><a name="list">3.</a> List NWS Watch/Warning/Advisories by State/WFO by Year</h3>
<br />
<p>This section generates a simple list of NWS Watch, Warning, and Advisories
by state and year.</p>
<br />

<form id="form3">
<div class="row">
    <div class="col-md-4">
        <input type="radio" name="by3" value="state" checked="checked" id="bystate"/>
        <label for="bystate">Select By State</label>
        <br /><select name="state" style="width: 100%" id="state3"></select></p>

        <p><input type="radio" name="by3" value="wfo" id="bywfo"/>
        <label for="bywfo">Select By WFO</label>
        <br /><select name="wfo" style="width: 100%" id="wfo3"></select></p>

        <p><label for="ph3">Select VTEC Phenomena:</label>
        <select name="ph" style="width: 100%" id="ph3"></select></p>

        <p><label for="sig3">Select VTEC Significance:</label>
        <select name="sig" style="width: 100%" id="sig3"></select></p>

        <p><label for="year3">Select Year:</label>
        <select name="year" style="width: 100%" id="year3"></select></p>

        <br /><button type="button" class="btn btn-default" id="button3">Update Table</button>
    </div>
    <div class="col-md-8">
    <h4 id="table3title"></h4>
    <button type="button" data-table="3" data-opt="excel" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to Excel...</button>
    <button type="button" data-table="3" data-opt="csv" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to CSV...</button>

    <table id="table3" data-order='[[ 3, "desc" ]]'>
    <thead>
    <tr><th>Event</th><th>WFO</th><th>Locations</th><th>Issued</th>
    <th>Expired</th></tr></thead>
    </table>
    </div>
</div><!-- ./row -->
</form><!-- ./form3 -->
EOF;
$t->render('full.phtml');
