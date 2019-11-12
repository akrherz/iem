<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 120);

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$uri = "http://iem.local/json/vtec_emergencies.py";
$data = file_get_contents($uri);
$json = json_decode($data, $assoc=TRUE);
$table = "";
foreach($json['events'] as $key => $val){
	$table .= sprintf("<tr><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td>".
			"<td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>",
			$val["year"],
			$val["wfo"], $val["uri"], $val["eventid"],
			$val["phenomena"], $val["significance"],
			$vtec_phenomena[$val["phenomena"]],
			$vtec_significance[$val["significance"]], 
			$val["issue"], $val["expire"]);
}

$t = new MyView();
$t->title = "Tornado + Flash Flood Emergencies Listing";
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.16/datatables.min.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.16/datatables.min.js'></script>
<script>
$('#makefancy').click(function(){
    $("#thetable table").DataTable();
});
</script>
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
any discrepancies, please <a href="/info/contacts.php">let us know</a>!  There is
an hour of caching involved with this listing, so anything within the past hour
may not immediately appear here.  You may wonder how events prior to the implementation
of VTEC have eventids.  These were retroactively generated and assigned by the IEM.
</div>

<p>Link to <a href="https://en.wikipedia.org/wiki/List_of_United_States_tornado_emergencies">Wikipedia List of United States tornado emergencies</a>.</p>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/vtec_emergencies.py
</code></p>

<p><button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead><tr><th>Year</th><th>WFO</th><th>Event ID</th><th>PH</th><th>SIG</th>
 <th>Event</th><th>Issue</th><th>Expire</th></tr>
</thead>		
{$table}
</table>
</div>

EOF;
$t->render("single.phtml");
?>