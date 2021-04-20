<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 151);
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";
$nt = new NetworkTable("WFO");

$clobber = isset($_REQUEST["clobber"]);
$wfo = isset($_REQUEST["wfo"]) ? strtoupper(substr($_REQUEST["wfo"],0,3)): null;
$phenomena = isset($_REQUEST["phenomena"]) ? strtoupper(substr($_REQUEST["phenomena"],0,2)): null;
$significance = isset($_REQUEST["significance"]) ? strtoupper(substr($_REQUEST["significance"],0,1)): null;
$wfoLimiter = "";
$wfoMsg = "Data for all WFOs shown";
if ($wfo){
	$wfoLimiter = " and wfo = '{$wfo}' ";
	$wfoMsg = "Data for only $wfo shown"; 
}

$p1 = make_select("phenomena", $phenomena, $vtec_phenomena);
$s1 = make_select("significance", $significance, $vtec_significance);

$t = new MyView();
$t->title = "VTEC Yearly Event Counts";

function get_data(){
	global $wfoLimiter;
	$dbconn = iemdb("postgis");
	
	$rs = pg_query("
			SELECT yr, phenomena, significance, count(*) from
			(SELECT distinct extract(year from issue) as yr, wfo,
			phenomena, significance, eventid from warnings WHERE
			significance is not null and phenomena is not null and
			issue > '1980-01-01' $wfoLimiter) as foo
			GROUP by yr, phenomena, significance
	");
	
	$data = Array();
	$pcodes = Array();
	for ($i=0;$row=pg_fetch_assoc($rs);$i++){
		$yr = $row["yr"];
		if (! array_key_exists($yr, $data)){
			$data[$yr] = Array();
		}
		$key = sprintf("%s.%s", $row["phenomena"], $row["significance"]);
		$pcodes[$key] = 1;
		$data[$yr][$key] = $row["count"];
	}
	return Array($data, $pcodes);
}

function get_data2(){
	global $phenomena, $significance;
	$dbconn = iemdb("postgis");

	$rs = pg_query("
		WITH data as (
			SELECT distinct wfo, eventid, extract(year from issue) as yr
			from warnings where phenomena = '$phenomena' and
			significance = '$significance'
		)
		SELECT wfo, yr, count(*) from data GROUP by wfo, yr
	");

	$data = Array();
	for ($i=0;$row=pg_fetch_assoc($rs);$i++){
		$yr = $row["yr"];
		if (! array_key_exists($yr, $data)){
			$data[$yr] = Array();
		}
		$data[$yr][$row["wfo"]] = $row["count"];
	}
	return $data;
}

/* see if memcache has our data */
$memcache = new Memcached();
$memcache->addServer('iem-memcached', 11211);
if (is_null($phenomena) || is_null($significance)){
	$data = $memcache->get("vtec_counts_data_$wfo");
	$pcodes = $memcache->get("vtec_counts_pcodes_$wfo");
	$cachedwarning = '<div class="alert alert-warning">This information was cached
				within the past 24 hours and may not be up to the moment.</div>';
	if ($clobber || !$data){
		list($data, $pcodes) = get_data();
		$memcache->set("vtec_counts_data_$wfo", $data, 86400);
		$memcache->set("vtec_counts_pcodes_$wfo", $pcodes, 86400);
		$cachedwarning = '';
	}
	
	$table = <<<EOF
	<table class="table table-striped">
	<thead><tr><th>P</th><th>S</th><th>Phenomena</th><th>Significance</th>
EOF;
	$years = array_keys($data);
	asort($years);
	foreach($years as $i => $yr){
		$table .= "<th>{$yr}</th>";
	}
	$table .= "</tr></thead>\n";
	
	$codes = array_keys($pcodes);
	asort($codes);
	foreach($codes as $j => $code){
		list($phenomena, $significance) = explode(".", $code);
		$table .= sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>",
				$phenomena, $significance, @$vtec_phenomena[$phenomena],
				@$vtec_significance[$significance]);
	
		foreach($years as $i => $yr){
			if (array_key_exists($code, $data[$yr])){
				$table .= sprintf("<td>%s</td>", $data[$yr][$code]);
			} else {
				$table .= "<td>0</td>";
			}
		}
		$table .= "</tr>";
	}
	$table .= "</table>";
} else {
	// Logic for by WFO by year
	$memkey = "vtec_counts_data_{$phenomena}_{$significance}";
	$data = $memcache->get($memkey);
	$cachedwarning = '<div class="alert alert-warning">This information was cached
				within the past 24 hours and may not be up to the moment.</div>';
	if ($clobber || !$data){
		$data = get_data2();
		$memcache->set($memkey, $data, 86400);
		$cachedwarning = '';
	}
	
	$table = <<<EOF
	<table class="table table-striped">
	<thead><tr><th>WFO</th><th>WFO Name</th>
EOF;
	$years = array_keys($data);
	asort($years);
	foreach($years as $i => $yr){
		$table .= "<th>{$yr}</th>";
	}
	$table .= "</tr></thead>\n";

	foreach($nt->table as $key => $val){
		$table .= sprintf("<tr><td>%s</td><td>%s</td>",
				$key, $val["name"]);
		foreach($years as $i => $yr){
			if (array_key_exists($key, $data[$yr])){
				$table .= sprintf("<td>%s</td>", $data[$yr][$key]);
			} else {
				$table .= "<td>0</td>";
			}
		}
		$table .= "</tr>";
	}
	$table .= "</table>";
	$wfoMsg = sprintf("%s.%s (%s %s) Event Counts by WFO", 
			$phenomena, $significance,
			$vtec_phenomena[$phenomena], $vtec_significance[$significance]);
}

$content = <<<EOF
<ol class="breadcrumb">
<li><a href="/nws/">NWS Resources</a></li>
<li class="active">VTEC Warning Counts by Year/WFO</li>
</ol>

<p>This page presents the number of VTEC events issued by either all of the
NWS or a selected WFO.  These numbers are based on the IEM maintained archive
and are not official.  Please be careful of the presentation of zeros, as 
some VTEC products were only recently added and don't go back prior to 2005.
The IEM retrospectively assigned VTEC events to some warnings prior to 
implementation in fall 2005.  Note: the numbers shown are the unique combinations
of VTEC event ids and WFO, so a single tornado watch event issued by four
WFOs would count as four in this summary, when summarizing all WFOs!</p>
		
<div class="alert alert-info">Hopefully, you can copy/paste this table into
your favorite spreadsheet program for further analysis...</div>
		
$cachedwarning
		
<p><h4>Option 1: All VTEC Events by Year</h4>
<form method="GET" name="wfo">
Limit Numbers by WFO: 
EOF;
$content .= "<select name=\"wfo\">
 <option value=\"ALL\" SELECTED>All Available</option>";
foreach($nt->table as $key => $value){
	$content .= "<option value='$key'>[$key] ". $value["name"] ."</option>\n";
}
$content .= <<<EOF
</select>
	<input type="submit" value="Generate Table">
</form>

<p><h4>Option 2: Count of One VTEC Phenomena and Significance by WFO</h4>
<form method="GET" name="wfo2">
{$p1} {$s1}
<input type="submit" value="Generate Table">
</form>

<h4>$wfoMsg</h4>

$table 

EOF;
$t->content = $content;
$t->render("single.phtml");
?>