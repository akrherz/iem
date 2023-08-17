<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 137);

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$year = get_int404("year", date("Y"));
$uri = sprintf("http://iem.local/json/watches.py?year=%s", $year);
$data = file_get_contents($uri);
$json = json_decode($data, $assoc = TRUE);
$table = "";
foreach ($json['events'] as $key => $val) {
    $spclink = sprintf(
        '<a target="_blank" href="https://www.spc.noaa.gov/products/watch/' .
            '%s/ww%04.0f.html">%s %s</a>',
        $val['year'],
        $val['num'],
        $val["type"],
        $val['num']
    );
    $table .= sprintf(
        "<tr><td>%s</td><td>%s%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $spclink,
        ($val["is_pds"]) ? ' <span class="badge badge-danger">PDS</span>' : "",
        $val["states"],
        $val["issue"],
        $val["expire"],
        $val["tornadoes_1m_strong"],
        $val["hail_1m_2inch"],
        $val["max_hail_size"],
        $val["max_wind_gust_knots"],
    );
}
$yearselect = yearSelect(1997, $year, "year");
$t = new MyView();
$t->title = "SPC Watches Listing";
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script>
$('#makefancy').click(function(){
    $("#thetable table").DataTable();
});
</script>
EOM;


$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">SPC Watch Listing</li>
</ol>
<h3>Yearly Listing of SPC Watches</h3>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/watches.py?year=$year</code></p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/nws/pds_watches.php">PDS Watches</a>
&nbsp;
</p>

<form method="GET" action="/nws/watches.php" name="ys">
<div class="form-group">

    <label for="year">Select Year</label>
    $yearselect
    <button type="submit">Update Table</button>
</div>
</form>

<p><button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead class="sticky"><tr><th>Year</th><th>Watch Num</th><th>State(s)</th><th>Issued</th>
<th>Expired</th><th>Prob EF2+ Tor</th><th>Prob Hail 2+in</th><th>Max Hail Size</th>
<th>Max Wind Gust kts</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>

EOF;
$t->render("full.phtml");
