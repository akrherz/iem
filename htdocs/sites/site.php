<?php
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";
force_https();
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/sites.php";
require_once "../../include/iemprop.php";
$OL = "10.6.1";
$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$alertmsg = "";
if (
    isset($_GET["lat"]) &&
    $_GET["lat"] != "move marker" &&
    floatval($_GET["lat"]) != 0 &&
    floatval($_GET["lat"]) != 1 &&
    floatval($_GET["lat"]) != -1 &&
    floatval($_GET["lon"]) != 0 &&
    floatval($_GET["lon"]) != 1 &&
    floatval($_GET["lon"]) != -1
) {
    $client_ip = getClientIp();
    // Log the request so to effectively do some DOS protection.
    $pgconn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $pgconn,
        "INSERT into weblog ".
            "(client_addr, uri, referer, http_status, x_forwarded_for) " .
            "VALUES ($1, $2, $3, $4, $5)"
    );
    pg_execute(
        $pgconn,
        $stname,
        array(
            $client_ip,
            "/sites/site.php?network={$network}&station={$station}",
            $_SERVER["HTTP_REFERER"],
            404,
            $_SERVER["HTTP_X_FORWARDED_FOR"]
        )
    );

    $newlat = floatval($_GET["lat"]);
    $newlon = floatval($_GET["lon"]);
    $email = isset($_GET["email"]) ? xssafe($_GET["email"]) : 'n/a';
    $name = isset($_GET["name"]) ? xssafe($_GET["name"]) : "n/a";
    $delta = (
        ($newlat - $metadata["lat"]) ** 2 +
        ($newlon - $metadata["lon"]) ** 2) ** 0.5;
    $msg = <<<EOM
IEM Sites Move Request
======================
> REMOTE_ADDR: {$client_ip}
> ID:          {$station}
> NAME:        {$name} OLD: {$metadata["name"]}
> NETWORK:     {$network}
> LON:         {$newlon} OLD: {$metadata["lon"]}
> LAT:         {$newlat} OLD: {$metadata["lat"]}
> EMAIL:       {$email}

Review with suggested location: {$EXTERNAL_BASEURL}/sites/site.php?network={$network}&station={$station}&suggested_lat={$newlat}&suggested_lon={$newlon}
Original location: {$EXTERNAL_BASEURL}/sites/site.php?network={$network}&station={$station}
EOM;
    if (($delta < 0.5) || (strpos($email, '@') > 0)) {
       mail("akrherz@iastate.edu", "Please move {$station} {$network}", $msg);
    }
    // We are doing a GET request, so we don't want folks to bookmark this
    header("Location: site.php?station={$station}&network={$network}&moved=1&suggested_lat={$newlat}&suggested_lon={$newlon}");
    exit();
}
if (isset($_GET["moved"])) {
    $moved_lat = isset($_GET["suggested_lat"]) ? sprintf("%.5f", floatval($_GET["suggested_lat"])) : null;
    $moved_lon = isset($_GET["suggested_lon"]) ? sprintf("%.5f", floatval($_GET["suggested_lon"])) : null;
    
    $coord_info = "";
    if ($moved_lat && $moved_lon) {
        $coord_info = " The red circle on the map shows your suggested location (Lat: {$moved_lat}, Lon: {$moved_lon}).";
    }
    
    $alertmsg = <<<EOM
<div class="alert alert-success">Thanks! Your suggested move was submitted for
evaluation.{$coord_info}</div>
EOM;
}

$lat = sprintf("%.5f", $metadata["lat"]);
$lon = sprintf("%.5f", $metadata["lon"]);

// Check for suggested coordinates
$suggested_lat = isset($_GET["suggested_lat"]) ? sprintf("%.5f", floatval($_GET["suggested_lat"])) : null;
$suggested_lon = isset($_GET["suggested_lon"]) ? sprintf("%.5f", floatval($_GET["suggested_lon"])) : null;

$suggested_coordinates_info = "";
if ($suggested_lat && $suggested_lon) {
    $suggested_coordinates_info = <<<EOM
<div class="alert alert-info">
<strong>Suggested Location Review:</strong> The blue marker shows the current database location, 
and the red circle shows a suggested new location (Lat: {$suggested_lat}, Lon: {$suggested_lon}) 
submitted for review.
</div>
EOM;
}

$t = new MyView();
$t->title = sprintf("Site Info: %s %s", $station, $metadata["name"]);
$t->headextra = <<<EOM
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script type="text/javascript" src="/js/olselect-lonlat.js"></script>
<script src="site.js" type="text/javascript"></script>
EOM;
$t->sites_current = "base";


function pretty_key($key)
{
    if ($key == "TRACKS_STATION") {
        return "Data tracks station";
    }
    return $key;
}
function pretty_value($key, $value)
{
    if ($key == "TRACKS_STATION") {
        $tokens = explode("|", $value);
        return sprintf(
            '<a href="/sites/site.php?station=%s&network=%s">%s [%s]</a>',
            $tokens[0],
            $tokens[1],
            $tokens[0],
            $tokens[1]
        );
    }
    return $value;
}

$attrtable = "";
if (sizeof($metadata["attributes"]) > 0) {
    $attrtable .= <<<EOM
    <h3>Station Attributes:</h3>
    <p><i>These are key value pairs used by the IEM to do data management.</i></p>
    <table class="table table-sm table-striped">
    <thead><tr><th>Key / Description</th><th>Value</th></tr></thead>
    <tbody>
EOM;
    foreach ($metadata["attributes"] as $key => $value) {
        $attrtable .= sprintf(
            "<tr><td>%s</td><td>%s</td></tr>",
            pretty_key($key),
            pretty_value($key, $value)
        );
    }
    $attrtable .= "</tbody></table>";
}
$threading = "";
if ((strpos($network, "CLIMATE") > 0) && (substr($station, 2, 1) == "T")) {
    $pgconn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $pgconn,
        "SELECT t.id, t.network, t.name, s.begin_date, s.end_date " .
            "from station_threading s " .
            "JOIN stations t on (s.source_iemid = t.iemid) WHERE s.iemid = $1 " .
            "ORDER by s.begin_date ASC"
    );
    $result = pg_execute($pgconn, $stname, array($metadata["iemid"]));
    if (pg_num_rows($result) > 0) {
        $threading = <<<EOM
<h3>Station Threading:</h3>
<p>This station threads together data from multiple stations to provide a
long term record for the location.</p>
<table class="table table-sm table-striped">
<thead><tr><th>Station</th><th>Begin Date</th><th>End Date</th></tr></thead>
<tbody>
EOM;
    }
    while ($row = pg_fetch_assoc($result)) {
        $threading .= sprintf(
            "<tr><td><a href=\"/sites/site.php?station=%s&network=%s\">%s (%s)</a></td><td>%s</td><td>%s</td></tr>",
            $row["id"],
            $row["network"],
            $row["name"],
            $row["id"],
            $row["begin_date"],
            $row["end_date"],
        );
    }
    if (pg_num_rows($result) > 0) {
        $threading .= "</tbody></table>";
    }
}

function df($val){
    if (is_null($val)){
        return "";
    }
    return $val->format("Y-m-d");
}
$ab = df($metadata["archive_begin"]);
$ae = df($metadata["archive_end"]);

$wigos = "";
if (! is_null($metadata["wigos"])){
    $wigos = sprintf(
        "<tr><th>WIGOS ID:</th>".
        "<td><a href=\"https://oscar.wmo.int/surface/#/search/station/".
        "stationReportDetails/%s\">%s</a></td></tr>",
        $metadata["wigos"],
        $metadata["wigos"]);
}

$t->content = <<<EOM

{$alertmsg}

<div class="row">
<div class="col-md-4">

<div class="card mb-4">
<div class="card-header">
<h4 class="mb-0">Station Information</h4>
</div>
<div class="card-body">
<table class="table table-sm table-striped">
<tr><th>IEM Internal ID:</th><td>{$metadata["iemid"]}</td></tr>
{$wigos}
<tr><th>Station Identifier:</th><td>{$station}</td></tr>
<tr><th>Station Name:</th><td>{$metadata["name"]}</td></tr>
<tr><th>Network:</th><td>{$network}</td></tr>
<tr><th>County:</th><td>{$metadata["county"]}</td></tr>
<tr><th>State:</th><td>{$metadata["state"]}</td></tr>
<tr><th>Latitude:</th><td>{$lat}</td></tr>
<tr><th>Longitude:</th><td>{$lon}</td></tr>
<tr><th>Elevation [m]:</th><td>{$metadata["elevation"]}</td></tr>
<tr><th>Time Zone:</th><td>{$metadata["tzname"]}</td></tr>
<tr><th>Archive Begin:</th><td>{$ab}</td></tr>
<tr><th>Archive End:</th><td>{$ae}</td></tr>
</table>
</div>
</div>

{$attrtable}

{$threading}

<div class="mb-3">
<a href="networks.php?station={$station}&amp;network={$network}" class="btn btn-primary">
<i class="fa fa-table"></i> View {$network} Network Table
</a>
</div>

</div>
<div class="col-md-8">

<div class="card">
<div class="card-header">
<h4 class="mb-0">Station Location</h4>
</div>
<div class="card-body">

<div id="mymap" style="height: 400px; width: 100%;" 
data-initial-lat="{$lat}" 
data-initial-lon="{$lon}"
data-suggested-lat="{$suggested_lat}" 
data-suggested-lon="{$suggested_lon}"
data-lat-input="newlat"
data-lon-input="newlon"
data-precision="8"
data-zoom="14"
data-bingmapsapikey="{$BING_MAPS_API_KEY}"></div>

<div class="mt-3">
<h5>Location Update Request</h5>
<p><strong>Is the location shown for this station wrong?</strong></p>
<p>If so, please consider submitting a location submission by moving the marker
on the map and completing this form below.</p>

{$suggested_coordinates_info}

<form name="updatecoords" method="GET">
<input type="hidden" value="{$network}" name="network">
<input type="hidden" value="{$station}" name="station">

<div class="row mb-3">
<div class="col-md-6">
<label for="newlat" class="form-label">New Latitude:</label>
<input id="newlat" type="text" class="form-control" name="lat" placeholder="move marker" required>
</div>
<div class="col-md-6">
<label for="newlon" class="form-label">New Longitude:</label>
<input id="newlon" type="text" class="form-control" name="lon" placeholder="move marker" required>
</div>
</div>

<div class="mb-3">
<label for="email" class="form-label">Enter Your Email Address <small>[1]</small>:</label>
<input type="email" id="email" class="form-control" name="email" placeholder="optional" autocomplete="email">
</div>

<div class="mb-3">
<label for="name" class="form-label">Better Location Name?:</label>
<input type="text" id="name" class="form-control" name="name" value="{$metadata["name"]}" maxlength="100" />
</div>

<div class="alert alert-info">
<small>
<strong>[1]</strong> Your email address will not be shared nor will you be added to any
lists. The IEM developer will simply email you back after consideration of
this request.
</small>
</div>

<div class="alert alert-warning">
<strong>Note:</strong> If you are looking for a wind rose for a location
other than this, your only option on this website is to find the nearest station
with data.
</div>

<input type="submit" value="I am asking the location be updated." class="btn btn-warning">
</form>
</div>

</div>
</div>

</div>

EOM;
$t->render('sites.phtml');
