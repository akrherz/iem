<?php
/*
 * I am sourced by all pages on the "sites" website except the 'locate' 
 * frontend.
 */
 require_once "../../config/settings.inc.php";
 require_once "../../include/database.inc.php";
 require_once "../../include/station.php";
 require_once "../../include/forms.php";
 /* Make sure all is well! */
 $station = isset($_GET["station"]) ? substr(xssafe($_GET["station"]), 0, 20) : "";
 $network = isset($_GET["network"]) ? xssafe($_GET["network"]): "";
 
if ($station == ""){
 	header("Location: locate.php");
 	die();
 }
 
$st = new StationData($station, $network);
$cities = $st->table;

 if (! array_key_exists($station, $cities))
 {
 	// Attempt to help the user find this station
 	include_once "../../include/myview.php";
	$iemdb = iemdb("mesosite");
	$rs = pg_prepare($iemdb, "FIND", "SELECT id, name, network from stations ".
			"WHERE id = $1");
	$rs = pg_execute($iemdb, 'FIND', Array($station));
	if (pg_num_rows($rs) == 0){
		header("Location: locate.php");
		die();
	}
	$table = <<<EOF
<p>Sorry, the requested station identifier and network could not be found
	within the IEM database.  Here are other network matches for your 
	identifier provided.</p>

<table class="table table-ruled table-bordered">
<thead><tr><th>ID</th><th>Name</th><th>Network</th></tr></thead>
<tbody>
EOF;
	for($i=0; $row=pg_fetch_assoc($rs); $i++){
		$table .= sprintf("<tr><td>%s</td><td><a href=\"site.php?network=%s".
				"&amp;station=%s\">%s</a></td><td>%s</td></tr>", $row["id"],
				$row["network"], $row["id"], $row["name"], $row["network"]);
	}
	$table .= "</tbody></table>";
	$t = new MyView();
 	$t->title = "Sites";
 	$t->content = $table;
 	
 	$t->render("single.phtml");
 	die();
 }

 if (! isset($_GET["network"]) )
 {
    $network = $cities[$station]["network"];
 }
 $metadata = $cities[$station];
?>
