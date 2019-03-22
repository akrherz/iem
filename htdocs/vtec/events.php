<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 85);
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"], 0, 4): 'DMX';
$year = isset($_GET["year"]) ? intval($_GET["year"]) : intval(date("Y"));
$state = isset($_GET['state']) ? substr($_GET["state"], 0, 2): 'IA';
$which = isset($_GET["which"]) ? $_GET["which"]: 'wfo';

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

if ($which == 'wfo'){
	$service = "";
	$uri = sprintf("http://iem.local/json/vtec_events.py?wfo=%s&year=%s", 
	$wfo, $year);
} else {
	$service = "_bystate";
	$uri = sprintf("http://iem.local/json/vtec_events_bystate.py?state=%s&year=%s", 
	$state, $year);
}
$data = file_get_contents($uri);
$json = json_decode($data, $assoc=TRUE);
$table = "";
while(list($key, $val)=each($json['events'])){
	$table .= sprintf("<tr><td>%s</td><td><a href=\"%s\">%s</a></td>".
			"<td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>",
			$val["wfo"], $val["uri"], $val["eventid"],
			$val["phenomena"], $val["significance"],
			$vtec_phenomena[$val["phenomena"]],
			$vtec_significance[$val["significance"]], 
			$val["issue"], $val["expire"]);
}

$t = new MyView();
$t->title = "VTEC Event Listing for $wfo during $year";
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
$yselect = yearSelect2(2005, $year, 'year');
$wfoselect = networkSelect("WFO", $wfo, array(), "wfo");
$stselect = stateSelect("state", $state);

$wchecked = ($which == 'wfo') ? "CHECKED": "";
$schecked = ($which == 'state') ? "CHECKED": "";

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">NWS VTEC Event Listing</li>
</ol>
<h3>NWS VTEC Event ID Usage</h3>

<div class="alert alert-info">This page provides a listing of VTEC events
for a given forecast office or state and year.  There are a number of caveats to this
listing due to issues encountered processing NWS VTEC enabled products. Some
events may appear listed twice due to quirks with how this information 
is stored within the database.  Hopefully, you can copy/paste the table into
your favorite spreadsheet program for further usage!</div>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/vtec_events{$service}.py?wfo={$wfo}&amp;year={$year}
</code></p>

<form method="GET" action="events.php">

<table class="table table-bordered">
<thead>
<tr>
 <th><input type="radio" name="which" value="wfo" $wchecked> By WFO</input></th>
 <th><input type="radio" name="which" value="state" $schecked> By State</input></th>
 <th>Year</th>
</tr>
</thead>

<tbody>
<tr>
 <td> $wfoselect </td>
 <td> $stselect </td>
 <td> $yselect </td>
 <td><input type="submit" value="Generate Table"></td>
</tr>
</tbody>
</table>

</form>

<p><button id="makefancy">Make Table Interactive</button></p>

<div id="thetable">
<table class="table table-striped table-condensed">
<thead><tr><th>WFO</th><th>Event ID</th><th>PH</th><th>SIG</th><th>Event</th>
 <th>Issue</th><th>Expire</th></tr>
</thead>		
{$table}
</table>
</div>

EOF;
$t->render("single.phtml");
?>