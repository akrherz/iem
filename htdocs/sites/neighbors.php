<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
// boilerplate is used in rendering :/
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$server = "http://iem.local";
$uri = sprintf("/geojson/station_neighbors.py?station=%s&network=%s", $station, $network);

$resp = file_get_contents("{$server}{$uri}");
if ($resp === FALSE) {
    die("Failed to fetch data");
}
$jobj = json_decode($resp, $assoc=TRUE);

$table = <<<EOM
<table class="table table-striped">
<thead class="sticky">
<tr><th>Distance [km]</th><th>ID</th><th>Network</th><th>Station Name</th>
<th>Archive Start</th><th>Archive End</th></tr></thead>
<tbody>
EOM;
foreach ($jobj["features"] as $feature){
    $props = $feature["properties"];
    $table .= sprintf(
        "<tr><td>%.2f</td><td><a href=\"/sites/site.php?network=%s&station=%s\">%s</a></td>".
        "<td><a href=\"locate.php?network=%s\">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $props["distance_km"],
        $props["network"],
        $props["sid"],
        $props["sid"],
        $props["network"],
        $props["network"],
        $props["sname"],
        $props["archive_begin"],
        $props["archive_end"]
    );

}

$table .= "</tbody></table>";

$t = new MyView();
$t->title = "Site Neighbors";
$t->sites_current = "neighbors";

$t->content = <<<EOM
<h3>Neighboring Stations</h3>
<p>The following is a list of IEM tracked stations within roughly a 0.25 degree
radius circle from the station location. Click on the site identifier
for more information. This <a href="/geojson/station_neighbors.py?help">GeoJSON webservice</a> provided
the data for this page. </p>

{$table}
EOM;
$t->render('sites.phtml');
