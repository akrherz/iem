<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 6);
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$pgconn = iemdb("mesosite");

$network = isset($_GET['network']) ? xssafe($_GET['network']): 'IA_ASOS';

if ($network == '_ALL_'){
	$sql = "SELECT *,
            ST_x(geom) as longitude, ST_y(geom) as latitude from stations
            WHERE online = 'y' and '_ALL_' = $1 ORDER by name";
} else if (isset($_GET["special"]) && $_GET["special"] == 'allasos'){
	$sql = "SELECT *,
            ST_x(geom) as longitude, ST_y(geom) as latitude from stations
            WHERE online = 'y' and
			(network ~* 'ASOS' or network = 'AWOS') and
			'IA_ASOS' = $1 ORDER by name";
	$network = "IA_ASOS";
} else {
	$sql = "SELECT *,
            ST_x(geom) as longitude, ST_y(geom) as latitude from stations
            WHERE network = $1 ORDER by name";
}
$rs = pg_prepare($pgconn, "NTSELECT", $sql);

$format = isset($_GET['format']) ? xssafe($_GET['format']): 'html';
$nohtml = isset($_GET['nohtml']);

$table = "";
if (strlen($network) > 0){
	$result = pg_execute($pgconn, "NTSELECT", Array($network) );
	if ($format == "html"){
		$table .= "<p><table class=\"table table-striped\">\n";
		$table .= "<caption><b>". $network ." Network</b></caption>\n";
		$table .= <<<EOM
<thead>
<tr>
<th>ID</th><th>Station Name</td><th>Latitude<sup>1</sup></th>
<th>Longitude<sup>1</sup></th><th>Elevation [m]</th>
<th>Archive Begins</th><th>Archive Ends</th><th>IEM Network</th>
</tr>
</thead>
EOM;
		for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
			$table .= "<tr>\n
			  <td><a href=\"site.php?station=". $row["id"] ."&amp;network=". $row["network"] ."\">". $row["id"] ."</a></td>
			  <td>". $row["name"] ."</td>
			  <td>". round($row["latitude"],5) . "</td>
			  <td>". round($row["longitude"],5) . "</td>
			  <td>". $row["elevation"]. "</td>
			  <td>". $row["archive_begin"]. "</td>
			  <td>". $row["archive_end"]. "</td>
			  <td><a href=\"locate.php?network=". $row["network"] ."\">". $row["network"]. "</a></td>
			  </tr>";
		}
		$table .= "</table>\n";

	} else if ($format == "csv") {
		if (! $nohtml) $table .= "<p><b>". $network ." Network</b></p>\n";
		if (! $nohtml) $table .= "<pre>\n";
		$table .= "stid,station_name,lat,lon,elev,begints,iem_network\n";
		for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
			$table .= $row["id"] .","
					. $row["name"] .","
					. round($row["latitude"],5). ","
					. round($row["longitude"],5). ","
					. $row["elevation"]. ","
					. $row["archive_begin"]. ","
					. $row["network"]. "\n";
		}
		if (! $nohtml)  $table .= "</pre>\n";
	}
	else if ($format == "shapefile") {

		/* Create SHP,DBF bases */
		$filePre = "${network}_locs";
		if (! is_file("/var/webtmp/{$filePre}.zip")){
			$shpFname = "/var/webtmp/$filePre";
			@unlink($shpFname.".shp");
			@unlink($shpFname.".shx");
			@unlink($shpFname.".dbf");
			@unlink($shpFname.".zip");
			$shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
			$dbfFile = dbase_create( $shpFname.".dbf", array(
					array("ID", "C", 6),
					array("NAME", "C", 50),
					array("NETWORK","C",20),
					array("BEGINTS","C",16),
			));
	
			for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
				$pt = ms_newPointobj();
				$pt->setXY( $row["longitude"], $row["latitude"], 0);
				$shpFile->addPoint($pt);
	
				dbase_add_record($dbfFile, array(
					$row["id"],
					$row["name"],
					$row["network"],
					substr($row["archive_begin"],0,16)));
			}
			unset($shpFile);
			dbase_close($dbfFile);
			chdir("/var/webtmp/");
			copy("/opt/iem/data/gis/meta/4326.prj", $filePre.".prj");
			popen("zip ".$filePre.".zip ".$filePre.".shp ".$filePre.".shx ".$filePre.".dbf ".$filePre.".prj", 'r');
		}
		$table .= "Shapefile Generation Complete.<br>";
		$table .= "Please download this <a href=\"/tmp/".$filePre.".zip\">zipfile</a>.";
		chdir("/opt/iem/htdocs/sites/");
}
else if ($format == "awips") {
	if (! $nohtml) $table .= "<pre>\n";
	for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
		$table .= sprintf("%s|%s|%-30s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["elevation"], $row["latitude"], $row["longitude"]);
	} // End of for
	if (! $nohtml) $table .= "</pre>\n";
}

else if ($format == "madis") {
	if (! $nohtml) $table .= "<pre>\n";

	for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
		if (substr($row["network"],0,4) == "KCCI") $row["network"] = "KCCI-TV";
		if (substr($row["network"],0,4) == "KELO") $row["network"] = "KELO-TV";
		if (substr($row["network"],0,4) == "KIMT") $row["network"] = "KIMT-TV";
		$table .= sprintf("%s|%s|%-39s%-11s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["network"], $row["elevation"], $row["latitude"], $row["longitude"]);
	} // End of for
	if (! $nohtml) $table .= "</pre>\n";
}

else if ($format == "gempak") {
	if (! $nohtml) $table .= "<pre>\n";
	for ($i=0; $row = @pg_fetch_array($result,$i); $i++) {
		$table .= str_pad($row["id"], 9)
		.  str_pad($row["synop"], 7)
		.  str_pad($row["name"], 33)
		.  str_pad($row["state"], 3)
		.  str_pad($row["country"], 2)
		.  sprintf("%6.0f", $row["latitude"] * 100)
		.  sprintf("%7.0f", $row["longitude"] * 100)
		.  sprintf("%6.0f", $row["elevation"])
		. "\n";
	}
	if (! $nohtml) $table .= "</pre>\n";
}
}


if (! $nohtml || $format == 'shapefile') {
	$t = new MyView();	
	$t->title = "Network Station Tables";
	$t->thispage = "iem-networks";
	$page = 'full.phtml';
	$sextra = "";
	if (isset($_REQUEST['station'])){
		$t->sites_current = "tables";
		include("setup.php");
		$page = 'sites.phtml';
		$sextra = sprintf("<input type=\"hidden\" value=\"%s\" name=\"station\">",
			xssafe($_REQUEST["station"]));
	}

	$ar = Array(
		"html" => "HTML Table",
		"csv" => "Comma Delimited",
		"shapefile" => "ESRI Shapefile",
		"gempak" => "GEMPAK Station Table",
		"awips" => "AWIPS Station Table",
		"madis" => "MADIS Station Table"
	);
	$fselect = make_select("format", $format, $ar);
	$nselect = selectNetwork($network, Array("_ALL_"=>"All Networks"));
	$t->content = <<<EOF
<h3>Network Location Tables</h3>

<div class="well pull-right">
<a href="new-rss.php"><img src="/images/rss.gif" style="border: 0px;" alt="RSS" /></a> Feed of newly 
added stations.

<br /><strong>Special Table Requests</strong>
<ul>
 <li><a href="networks.php?special=allasos&format=gempak&nohtml">Global METAR in GEMPAK Format</a></li>
</ul>
</div>


<p>With this form, you can generate a station table for any
of the networks listed below.  If there is a particular format for a station
table that you need, please <a href="/info/contacts.php">let us know</a>.</p>

<form method="GET" action="networks.php" name="networkSelect">
<table>
<tr>
  <th>Select Observing Network:</th>
  <td>{$nselect}</td>
</tr>
<tr>
  <th>Select Format:</th>
<td>
{$fselect}
</td></tr>

<tr>
 <td colspan="2"><input type="checkbox" name="nohtml">Just Table, no HTML</td></tr>

<tr><td colspan="2">
<input type="submit" value="Create Table">
</form>
</td></tr>
</table>

{$table}
<p><h3>Notes</h3>
<ol>
<li>Latitude and Longitude values are in decimal degrees.</li>
<li>Elevation is expressed in meters above sea level.</li>
</ol>
EOF;
	$t->render($page);
} else{
	header("Content-type: text/plain");
	echo $table;
}
?>
