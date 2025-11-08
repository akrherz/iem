<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 6);
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/network.php";
require_once "../../include/vendor/mapscript.php";

$pgconn = iemdb("mesosite");

$network = get_str404('network', 'IA_ASOS');

$extra_networks = array(
    "_ALL_" => "All Networks",
    "HAS_HML" => "Stations with HML Data",
);

function attrs2str($arr)
{
    $s = "";
    if (is_array($arr)) {
        foreach ($arr as $key => $value) {
            if ($key != ""){  // Good grief PHP
                $s .= sprintf("%s=%s<br />", $key, $value);
            }
        }
    }
    return $s;
}
function pretty_date($val, $fmt = "M d, Y")
{
    if (is_null($val)) {
        return "";
    }
    if (is_string($val)) {
        $val = new DateTime($val);
    }
    return $val->format($fmt);
}

if ($network == '_ALL_') {
    // Too much memory at the moment
    $rs = pg_query(
        $pgconn,
        "SELECT id, name, elevation, archive_begin, archive_end, network, " .
            "ST_x(geom) as lon, ST_y(geom) as lat, null as attributes, state, " .
            "synop, country from stations WHERE online = 't' and ".
            "network !~* '_COCORAHS' ORDER by name"
    );
    $cities = array();
    while ($row = pg_fetch_assoc($rs)) {
        $cities[$row["id"]] = $row;
    }
} else if (get_str404("special", null) == 'allasos') {
    $rs = pg_query(
        $pgconn,
        "SELECT id, name, elevation, archive_begin, archive_end, network, " .
            "ST_x(geom) as lon, ST_y(geom) as lat, null as attributes, state, " .
            "synop, country from stations WHERE online and " .
            "network ~* 'ASOS' ORDER by name"
    );
    $cities = array();
    while ($row = pg_fetch_assoc($rs)) {
        $cities[$row["id"]] = $row;
    }
} else if (get_str404("special", null) == 'alldcp') {
    $rs = pg_query(
        $pgconn,
        "SELECT id, name, elevation, archive_begin, archive_end, network, " .
            "ST_x(geom) as lon, ST_y(geom) as lat, null as attributes, state, " .
            "synop, country from stations WHERE online and " .
            "network ~* 'DCP' ORDER by name"
    );
    $cities = array();
    while ($row = pg_fetch_assoc($rs)) {
        $cities[$row["id"]] = $row;
    }
} else {
    $resp = file_get_contents(
        "{$INTERNAL_BASEURL}/geojson/network/{$network}.geojson");
    if ($resp === FALSE) {
        $cities = array();
    } else {
        $jobj = json_decode($resp, $assoc = TRUE);
        $cities = array();
        foreach ($jobj["features"] as $k => $v) {
            $props = $v["properties"];
            $cities[$props["sid"]] = Array(
                "id" => $props["sid"],
                "name" => $props["sname"],
                "elevation" => $props["elevation"],
                "archive_begin" => $props["archive_begin"],
                "archive_end" => $props["archive_end"],
                "network" => $props["network"],
                "lon" => $v["geometry"]["coordinates"][0],
                "lat" => $v["geometry"]["coordinates"][1],
                "attributes" => $props["attributes"],
                "state" => $props["state"],
                "synop" => $props["synop"],
                "country" => $props["country"],
                "attributes" => $props["attributes"],
            );
        }
    }
}

$format = get_str404('format', 'html');
$nohtml = array_key_exists('nohtml', $_GET);

$table = "";
if (strlen($network) > 0) {
    if ($format == "html") {
        $table .= "<div class=\"table-responsive\"><table class=\"table table-striped\">\n";
        $table .= "<caption><strong>" . $network . " Network</strong></caption>\n";
        $table .= <<<EOM
<thead class="table-dark sticky-top">
<tr>
<th>ID</th><th>Station Name</th><th>Latitude<sup>1</sup></th>
<th>Longitude<sup>1</sup></th><th>Elevation [m]</th>
<th>Archive Begins</th><th>Archive Ends</th><th>IEM Network</th>
<th>Attributes</th>
</tr>
</thead>
EOM;
        foreach ($cities as $sid => $row) {
            $table .= "<tr>\n
              <td><a href=\"site.php?station={$sid}&amp;network=" . $row["network"] . "\">{$sid}</a></td>
              <td>" . $row["name"] . "</td>
              <td>" . round($row["lat"], 5) . "</td>
              <td>" . round($row["lon"], 5) . "</td>
              <td>" . $row["elevation"] . "</td>
              <td>" . pretty_date($row["archive_begin"]) . "</td>
              <td>" . pretty_date($row["archive_end"]) . "</td>
              <td><a href=\"locate.php?network=" . $row["network"] . "\">" . $row["network"] . "</a></td>
              <td>" . attrs2str($row["attributes"]) . "</td>
              </tr>";
        }
        $table .= "</table></div>\n";
    } else if ($format == "csv") {
        if (!$nohtml) $table .= "<p><b>" . $network . " Network</b></p>\n";
        if (!$nohtml) $table .= "<pre>\n";
        $table .= "stid,station_name,lat,lon,elev,begints,endts,iem_network\n";
        foreach ($cities as $sid => $row) {
            $table .= $sid . ","
                . $row["name"] . ","
                . round($row["lat"], 5) . ","
                . round($row["lon"], 5) . ","
                . $row["elevation"] . ","
                . pretty_date($row["archive_begin"], 'Y-m-d H:i') . ","
                . pretty_date($row["archive_end"], 'Y-m-d H:i') . ","
                . $row["network"] . "\n";
        }
        if (!$nohtml)  $table .= "</pre>\n";
    } else if ($format == "shapefile") {

        /* Create SHP,DBF bases */
        $filePre = "{$network}_locs";
        $sufixes = Array("shp", "shx", "dbf", "zip");
        if (!is_file("/var/webtmp/{$filePre}.zip")) {
            $shpFname = "/var/webtmp/$filePre";
            foreach($sufixes as $key => $suff){
                $fn = "{$shpFname}.{$suff}";
                if (is_file($fn)) unlink($fn);
            }
            $shpFile = new shapeFileObj($shpFname, mapscript::MS_SHAPEFILE_POINT);
            $dbfFile = dbase_create($shpFname . ".dbf", array(
                array("ID", "C", 6),
                array("NAME", "C", 50),
                array("NETWORK", "C", 20),
                array("BEGINTS", "C", 16),
            ));

            foreach ($cities as $sid => $row) {
                $pt = new pointObj();
                $pt->setXY($row["lon"], $row["lat"], 0);
                $shpFile->addPoint($pt);

                dbase_add_record($dbfFile, array(
                    $row["id"],
                    $row["name"],
                    $row["network"],
                    pretty_date($row["archive_begin"], "Y-m-d"),
                ));
            }
            unset($shpFile);
            dbase_close($dbfFile);
            chdir("/var/webtmp/");
            copy("/opt/iem/data/gis/meta/4326.prj", $filePre . ".prj");
            popen("zip {$filePre}.zip {$filePre}.shp {$filePre}.shx {$filePre}.dbf {$filePre}.prj", 'r');
        }
        $table .= <<<EOM
<div class="alert alert-info">
Shapefile Generation Complete.<br>
Please download this <a href="/tmp/{$filePre}.zip">zipfile</a>.
</div>
EOM;
        chdir("/opt/iem/htdocs/sites/");
    } else if ($format == "awips") {
        if (!$nohtml) $table .= "<pre>\n";
        foreach ($cities as $sid => $row) {
            $table .= sprintf("%s|%s|%-30s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["elevation"], $row["lat"], $row["lon"]);
        } // End of for
        if (!$nohtml) $table .= "</pre>\n";
    } else if ($format == "madis") {
        if (!$nohtml) $table .= "<pre>\n";

        foreach ($cities as $sid => $row) {
            if (substr($row["network"], 0, 4) == "KCCI") $row["network"] = "KCCI-TV";
            if (substr($row["network"], 0, 4) == "KELO") $row["network"] = "KELO-TV";
            if (substr($row["network"], 0, 4) == "KIMT") $row["network"] = "KIMT-TV";
            $table .= sprintf("%s|%s|%-39s%-11s|%4.1f|%2.5f|%3.5f|GMT|||1||||\n", $row["id"], $row["id"], $row["name"], $row["network"], $row["elevation"], $row["lat"], $row["lon"]);
        } // End of for
        if (!$nohtml) $table .= "</pre>\n";
    } else if ($format == "gempak") {
        if (!$nohtml) $table .= "<pre>\n";
        foreach ($cities as $sid => $row) {
            $table .= str_pad($row["id"], 9)
                .  str_pad(is_null($row["synop"]) ? "": $row["synop"], 7)
                .  str_pad($row["name"], 33)
                .  str_pad(is_null($row["state"]) ? "": $row["state"], 3)
                .  str_pad(is_null($row["country"]) ? "": $row["country"], 2)
                .  sprintf("%6.0f", $row["lat"] * 100)
                .  sprintf("%7.0f", $row["lon"] * 100)
                .  sprintf("%6.0f", $row["elevation"])
                . "\n";
        }
        if (!$nohtml) $table .= "</pre>\n";
    }
}


if (!$nohtml || $format == 'shapefile') {
    $t = new MyView();
    $t->iemselect2 = true;
    $t->title = "Network Station Tables";
    $page = 'full.phtml';
    $sextra = "";
    if (array_key_exists('station', $_REQUEST)) {
        $t->sites_current = "tables";
        require_once "../../include/sites.php";
        $ctx = get_sites_context();
        $station = $ctx->station;
        $network = $ctx->network;
        $metadata = $ctx->metadata;

        $page = 'sites.phtml';
        $sextra = sprintf(
            "<input type=\"hidden\" value=\"%s\" name=\"station\">",
            xssafe($_REQUEST["station"])
        );
    }

    $ar = array(
        "html" => "HTML Table",
        "csv" => "Comma Delimited",
        "shapefile" => "ESRI Shapefile",
        "gempak" => "GEMPAK Station Table",
        "awips" => "AWIPS Station Table",
        "madis" => "MADIS Station Table"
    );
    $fselect = make_select("format", $format, $ar);
    $nselect = selectNetwork($network, $extra_networks);
    $t->content = <<<EOM
<div class="card mb-4">
<div class="card-header">
<h3 class="mb-0">Network Location Tables</h3>
</div>
<div class="card-body">

<div class="card float-end" style="width: 300px;">
<div class="card-body">
<a href="new-rss.php"><img src="/images/rss.gif" style="border: 0px;" alt="RSS" /></a> Feed of newly
added stations.

<div class="mt-3">
<strong>Special Table Requests</strong>
<ul class="list-unstyled mt-2">
 <li><a href="networks.php?special=allasos&format=gempak&nohtml">Global METAR in GEMPAK Format</a></li>
 <li><a href="networks.php?special=allasos&format=csv&nohtml">Global METAR in CSV Format</a></li>
 <li><a href="/geojson/network/AZOS.geojson">Global METAR/ASOS in GeoJSON</a></li>
 <li><a href="networks.php?special=alldcp&format=csv&nohtml">All DCPs in CSV Format</a></li>
 <li><a href="networks.php?network=HAS_HML">Sites with HML Coverage</a></li>
</ul>
</div>
</div>
</div>


<p>With this form, you can generate a station table for any
of the networks listed below.  If there is a particular format for a station
table that you need, please <a href="/info/contacts.php">let us know</a>.</p>

<form method="GET" action="networks.php" name="networkSelect">
{$sextra}

<div class="row mb-3">
<div class="col-md-6">
<label for="network" class="form-label"><strong>Select Observing Network:</strong></label>
{$nselect}
</div>
<div class="col-md-6">
<label for="format" class="form-label"><strong>Select Format:</strong></label>
{$fselect}
</div>
</div>

<div class="form-check mb-3">
<input class="form-check-input" type="checkbox" name="nohtml" id="nohtml">
<label class="form-check-label" for="nohtml">Just Table, no HTML</label>
</div>

<div class="mb-3">
<input type="submit" value="Create Table" class="btn btn-primary">
</div>

</form>
</div>
</div>

{$table}
<div class="card">
<div class="card-header">
<h3 class="mb-0">Notes</h3>
</div>
<div class="card-body">
<ol>
<li>Latitude and Longitude values are in decimal degrees.</li>
<li>Elevation is expressed in meters above sea level.</li>
</ol>
</div>
</div>
EOM;
    $t->render($page);
} else {
    header("Content-type: text/plain");
    echo $table;
}
