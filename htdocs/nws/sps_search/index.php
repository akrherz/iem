<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 140);
require_once "../../../include/mlib.php";
force_https();
require_once "../../../include/myview.php";
require_once "../../../include/iemprop.php";
$t = new MyView();
$OL = "9.2.4";

$t->jsextra = <<<EOF
<script type="text/javascript" src="/js/mapping.js"></script>
<script src="/vendor/jquery-datatables/1.10.20/datatables.min.js"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src="/vendor/select2/4.1.0rc0/select2.min.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script type="text/javascript" src="/js/olselect-lonlat.js"></script>
<script type="text/javascript" src="search.js?v=2"></script>
EOF;

$t->headextra = <<<EOF
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
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
$t->title = "Special Weather Statement (SPS) Search by Point";

$t->content = <<<EOF
<p>
<ul class="breadcrumb">
<li><a href="/nws/">NWS Mainpage</a></li>
<li class="active">SPS Search by Point</li>
</ul>
</p>

<p>This page allows a point based search of NWS Special Weather Statements
(SPS) that <strong>contained a polygon</strong>.  These polygons provide a
latitude/longitude specific area that the SPS is valid for.  Not all SPS
products have a polygon, so this interface <strong>does not show them</strong>.
</p>

<p>
<strong>Related:</strong> &nbsp;
<a class="btn btn-primary" href="/request/gis/sps.phtml">SPS Download</a> &nbsp;
<a class="btn btn-primary" href="/wx/afos/p.php?pil=SPSDMX">SPS Text Download</a>
</p>

<br clear="all" />
<div class="row">
    <div class="col-md-4">
        <p><strong>Either enter coordinates manually:</strong><br />
        <i>Latitude (deg N):</i> <input size="8" id="lat" value="41.53"><br />
        <i>Longitude (deg E):</i> <input size="8" id="lon" value="-93.653">
        <br /><label for="sdate">Start Date:
            <input name="sdate" type="text" id="sdate"></label>
            <br /><label for="edate">End Date:
            <input name="edate" type="text" id="edate"></label>
    
        <button type="button" class="btn btn-default" id="manualpt">Update</button>
        </p>
        <p><strong>Or drag marker to select coordinate:</strong><br />
        <div id="map" class="map"></div>
    </div>
    <div class="col-md-8">
    <h4 id="table1title"></h4>
    <button type="button" data-table="1" data-opt="excel" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to Excel...</button>
    <button type="button" data-table="1" data-opt="csv" class="btn btn-default iemtool"><i class="fa fa-download"></i> Export to CSV...</button>

    <table id="table1" data-order='[[ 1, "desc" ]]'>
    <thead><tr>
    <th>Link</th>
    <th>Issue</th>
    <th>Landspout Tag</th>
    <th>Waterspout Tag</th>
    <th>Max Hail Size (in)</th>
    <th>Max Wind Gust (mph)</th>
    </tr></thead>
    </table>
    </div>
</div>

</form><!-- ./form2 -->

EOF;
$t->render('full.phtml');
