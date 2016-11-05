<?php 
include_once "../../config/settings.inc.php";
define("IEM_APPID", 85);
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"], 0, 4): 'DMX';
$year = isset($_GET["year"]) ? intval($_GET["year"]) : intval(date("Y"));

include_once "../../include/myview.php";
include_once "../../include/vtec.php";
include_once "../../include/forms.php";
include_once "../../include/imagemaps.php";

$uri = sprintf("http://iem.local/json/vtec_events.py?wfo=%s&year=%s", 
		$wfo, $year);
$data = file_get_contents($uri);
$json = json_decode($data, $assoc=TRUE);
$table = "";
while(list($key, $val)=each($json['events'])){
	$table .= sprintf("<tr><td>%s</td><td><a href=\"%s\">%s</a></td>".
			"<td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>",
			$wfo, $val["uri"], $val["eventid"],
			$val["phenomena"], $val["significance"],
			$vtec_phenomena[$val["phenomena"]],
			$vtec_significance[$val["significance"]], 
			$val["issue"], $val["expire"]);
}

$t = new MyView();
$t->title = "VTEC Event Listing for $wfo during $year";


$yselect = yearSelect2(2005, $year, 'year');
$wfoselect = networkSelect("WFO", $wfo, array(), "wfo");


$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">NWS VTEC Event Listing</li>
</ol>
<h3>NWS VTEC Event ID Usage</h3>

<div class="alert alert-info">This page provides a listing of VTEC events
for a given forecast office and year.  There are a number of caveats to this
listing due to issues encountered processing NWS VTEC enabled products. Some
events may appear listed twice due to quirks with how this information 
is stored within the database.  Hopefully, you can copy/paste the table into
your favorite spreadsheet program for further usage!</div>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>https://mesonet.agron.iastate.edu/json/vtec_events.py?wfo={$wfo}&amp;year={$year}
</code></p>

<form method="GET" action="events.php">
		Select WFO: $wfoselect
		Select Year: $yselect
		<input type="submit" value="Generate Table">
</form>
				
<table class="table table-striped table-condensed">
<thead><tr><th>WFO</th><th>Event ID</th><th>PH</th><th>SIG</th><th>Event</th>
 <th>Issue</th><th>Expire</th></tr>
</thead>		
{$table}
</table>

EOF;
$t->render("single.phtml");
?>