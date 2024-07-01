<?php
/*
 * List out WPC National High/Low Data
 */
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 142);
require_once "../../../include/myview.php";
require_once "../../../include/imagemaps.php";
require_once "../../../include/mlib.php";
require_once "../../../include/forms.php";

$t = new MyView();
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

$state = isset($_REQUEST['state']) ? xssafe($_REQUEST['state']) : null;
$year = get_int404("year", date("Y"));
$opt = get_int404("opt", 0);

$t->title = "WPC National High Low Temperature";

$sselect = stateSelect($state);
$yselect = yearSelect(2008, $year);
$opts = Array(
    1 => "By State",
    0 => "By Year",
);
$oselect = make_select("opt", $opt, $opts);

$params = Array();
if ($opt == 1) {
    $arr["state"] = $state;
    $title = "Entries for state: {$state}";
} else {
    $arr["year"] = $year;
    $title = "Entries for year: {$year}";
}
$jobj = iemws_json("nws/wpc_national_hilo.json", $arr);

function write_entry($entry){
    return sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n",
        $entry["date"], $entry["N_val"],
        implode("<br />", $entry["N_names"]), $entry["X_val"],
        implode("<br />", $entry["X_names"]));
}

$thisdate = 0;
$entry = null;
$table = "";
if (sizeof($jobj["data"]) == 0){
    $table = '<tr><th colspan="5">No data found for query</th></tr>';
}
foreach ($jobj["data"] as $bogus => $row) {
    if ($row["date"] != $thisdate) {
        if (!is_null($entry)) $table .= write_entry($entry);
        $entry = Array(
            "date" => $row["date"],
            "X_val" => "",
            "X_names" => Array(),
            "N_val" => "",
            "N_names" => Array(),
        );
        $thisdate = $row["date"];
    }
    $key = $row["n_x"];
    $entry["{$key}_val"] = $row["value"];
    $entry["{$key}_names"][] = sprintf("(%s) %s %s", $row["station"], $row["name"], $row["state"]);
}
if (!is_null($entry)) $table .= write_entry($entry);

$yearselected = ($opt == 0) ? ' checked="checked" ': "";
$stateselected = ($opt == 1) ? ' checked="checked" ': "";
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="active">WPC National High Low</li>
</ol>

<p>The IEM maintains an archive of the <a href="https://www.wpc.ncep.noaa.gov/discussions/hpcdiscussions.php?disc=nathilo&version=0&fmt=reg">National High and Low Temperature</a>
product.  This product is disseminated over NOAAPort in an XML format and called
<a href="/wx/afos/p.php?pil=XTEUS">XTEUS</a>. This data presentation is powered
by an <a href="/api/1/docs#/nws/service_nws_wpc_national_hilo__fmt__get">IEM Web Service</a>.
The IEM archive begins on <strong>30 June 2008</strong>, but the data quality prior to 2011 has been a
bit suspect due to issues with the raw text product and other things that makes life
fun.</p>

<p><button id="makefancy">Make Table Interactive</button></p>

<form method="GET" name="changeme">
<table class="table table-condensed">
<tr>
<td>
<input type="radio" name="opt" value="0" {$yearselected} id="year">
<label for="year">Select by Year</label>:</strong>{$yselect}
</td>
<td>
<input type="radio" name="opt" value="1" {$stateselected} id="state">
<label for="state">Select by State</label>:</strong>
{$sselect}
<br />Only contiguous US State...
</td>
<td><input type="submit" value="Update Table"></td>
</tr>
</table>
</form>

<h3>{$title}</h3>

<div id="thetable">
<table class="table table-striped table-condensed table-bordered">
<thead class="sticky">
<tr><th>Date</th><th>Min &deg;F</th><th>Location(s)</th><th>Max &deg;F</th>
<th>Location(s)</tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>
EOF;
$t->render('full.phtml');
