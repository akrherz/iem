<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 136);

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$uri = "http://iem.local/json/watches.py?is_pds=1";
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
        "<tr><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $spclink,
        $val["states"],
        $val["issue"],
        $val["expire"],
        $val["tornadoes_1m_strong"],
        $val["hail_1m_2inch"],
        $val["max_hail_size"],
        $val["max_wind_gust_knots"],
    );
}

$t = new MyView();
$t->title = "Particularly Dangerous Situation SPC Watches Listing";
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
 <li class="active">Particularly Dangerous Situation Watches</li>
</ol>
<h3>Particularly Dangerous Situation SPC Watches</h3>

<div class="alert alert-info">This page presents the current
<strong>unofficial</strong> IEM
accounting of SPC watches that contain the special Particularly Dangerous Situation
phrasing.
</div>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/watches.py?is_pds=1</code></p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/vtec/emergencies.php">TOR/FFW Emergencies</a>
&nbsp;
<a class="btn btn-primary" href="/nws/watches.php">List Watches by Year</a>
&nbsp;
<a class="btn btn-primary" href="/vtec/pds.php">PDS Warnings</a>
&nbsp;
</p>

<p><button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead class="sticky">
<tr><th>Year</th><th>Watch Num</th><th>State(s)</th><th>Issued</th>
<th>Expired</th><th>Prob EF2+ Tor</th><th>Prob Hail 2+in</th>
<th>Max Hail Size</th>
<th>Max Wind Gust kts</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>

EOF;
$t->render("full.phtml");
