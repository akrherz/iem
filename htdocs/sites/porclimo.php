<?php
require_once "../../config/settings.inc.php";
require_once "../../include/mlib.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$t = new MyView();
$t->title = "Period of Record Daily Climatology";
$t->sites_current = "porclimo";

$arr = array(
    "station" => $station,
);
$json = iemws_json("/climodat/por_daily_climo.json", $arr);
if ($json === FALSE) {
    $json = array("data" => array());
}
$table = "";
foreach ($json["data"] as $key => $row) {
    $dt = new DateTime($row["date"]);
    $table .= sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $dt->format("M d"),
        $row["high_min"],
        $row["high_min_years"],
        $row["high_avg"],
        $row["high_max"],
        $row["high_max_years"],
        $row["low_min"],
        $row["low_min_years"],
        $row["low_avg"],
        $row["low_max"],
        $row["low_max_years"],
        $row["precip"],
        $row["precip_max"],
        $row["precip_max_years"]
    );
}
$t->content = <<<EOF

<p>This table presents a simple period-of-record summary for the current station.
This is simply based off of whatever daily data exists without any adjustments,
etc. The raw data is available as a 
<a href="/api/1/climodat/por_daily_climo.txt?station={$station}">CSV</a>.</p>

<table class="table table-striped table-condensed">
<thead class="sticky">
<tr><th>Day</th>
<th>Min High</th><th>Min High Year(s)</th><th>Avg High</th><th>Max High</th><th>Max High Year(s)</th>
<th>Min Low</th><th>Min Low Year(s)</th><th>Avg Low</th><th>Max Low</th><th>Max Low Year(s)</th>
<th>Precip</th><th>Max Precip</th><th>Max Precip Year(s)</th>
</tr>
</thead>
<tbody>
{$table}
</tbody>
</table>

EOF;
$t->render('sites.phtml');
