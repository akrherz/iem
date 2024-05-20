<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 122);

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$uri = "http://iem.local/json/vtec_pds.py";
$data = file_get_contents($uri);
$json = json_decode($data, $assoc = TRUE);
$table = "";
foreach ($json['events'] as $key => $val) {
    $table .= sprintf(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td>" .
            "<td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>",
        $val["year"],
        $val["wfo"],
        $val["states"],
        $val["uri"],
        $val["eventid"],
        $val["phenomena"],
        $val["significance"],
        $vtec_phenomena[$val["phenomena"]],
        $vtec_significance[$val["significance"]],
        $val["issue"],
        $val["expire"]
    );
}

$t = new MyView();
$t->title = "Particularly Dangerous Situation Tornado Warnings Listing";
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
 <li class="active">Particularly Dangerous Situation Warnings</li>
</ol>
<h3>Particularly Dangerous Situation Tornado / Flash Flood Warnings</h3>

<p>This page presents the current and
<strong>unofficial</strong> IEM
accounting of Warnings that contain the special Particularly Dangerous Situation
phrasing. This phrasing is the only key used to identify such events.  The phrasing
can occur in either the issuance and/or followup statements.</p>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/vtec_pds.py</code></p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="/vtec/emergencies.php">TOR/FFW Emergencies</a>
&nbsp;
<a class="btn btn-primary" href="/nws/pds_watches.php">SPC PDS Watches</a>
&nbsp;
</p>

<p>
This listing was generated at: <code>{$json['generated_at']}</code> and is
regenerated hourly. <button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead><tr><th>Year</th><th>WFO</th><th>State(s)</th><th>Event ID</th>
<th>PH</th><th>SIG</th><th>Event</th><th>Issue</th><th>Expire</th></tr>
</thead>
{$table}
</table>
</div>

EOF;
$t->render("full.phtml");
