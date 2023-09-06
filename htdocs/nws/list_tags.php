<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 77);
putenv("TZ=UTC");
date_default_timezone_set('UTC');
require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";

$t = new MyView();

$year = get_int404("year", date("Y"));
$wfo = isset($_REQUEST["wfo"]) ? xssafe($_REQUEST["wfo"]) : "DMX";
$opt = isset($_REQUEST["opt"]) ? xssafe($_REQUEST["opt"]) : "bywfo";
$damagetag = isset($_REQUEST["damagetag"]) ? xssafe($_REQUEST["damagetag"]) : "considerable";

$damagetags = array(
    "considerable" => "Considerable",
    "destructive" => "Destructive (SVR Only)",
    "catastrophic" => "Catastrophic",
);
if (!array_key_exists($damagetag, $damagetags)) {
    $damagetag = "considerable";
}

$bywfochecked = "";
$bydamagetagchecked = "";
if ($opt == "bywfo") {
    $bywfochecked = "checked";
    $jsonuri = sprintf(
        "http://iem.local/json/ibw_tags.py?wfo=%s&year=%s",
        $wfo,
        $year
    );
    $title = "NWS $wfo issued Impact Based Warning Tags for $year";
} else {
    $bydamagetagchecked = "checked";
    $jsonuri = sprintf(
        "http://iem.local/json/ibw_tags.py?damagetag=%s&year=%s",
        $damagetag,
        $year
    );
    $title = "NWS Damage Tags of $damagetag for $year";
}
$publicjsonuri = str_replace("http://iem.local", "https://mesonet.agron.iastate.edu", $jsonuri);

$t->title = $title;
$t->headextra = '
<link rel="stylesheet" type="text/css" href="/vendor/ext/3.4.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="/vendor/ext/3.4.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="/vendor/ext/3.4.1/ext-all.js"></script>
<script type="text/javascript" src="/vendor/ext/ux/TableGrid.js"></script>
<script>
Ext.onReady(function(){
    var btn = Ext.get("create-grid1");
    btn.on("click", function(){
        btn.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("svr", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

     var btn2 = Ext.get("create-grid2");
    btn2.on("click", function(){
        btn2.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("tor", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

    var btn3 = Ext.get("create-grid3");
    btn3.on("click", function(){
        btn3.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("ffw", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

    var btn4 = Ext.get("create-grid4");
    btn4.on("click", function(){
        btn4.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("smw", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once


});
</script>
';


function do_col1($row)
{
    if ($row["status"] == 'NEW') {
        return sprintf("<a href=\"%s\">%s</a>", $row['href'], $row["eventid"]);
    }
    $ptype = 'SVS';
    if ($row["phenomena"] == 'MA') $ptype = "MWS";
    elseif ($row["phenomena"] == 'FF') $ptype = "FFS";
    return sprintf("<a href=\"%s\">%s.%s</a>", $row['href'], $row["eventid"], $ptype);
}
function do_col2($row)
{
    if ($row["status"] == 'NEW') {
        return date("Y/m/d Hi", strtotime($row["issue"]));
    }
    return date("Y/m/d Hi", strtotime($row["polygon_begin"]));
}
function do_col3($row)
{
    if ($row["status"] == 'NEW') {
        return date("Hi", strtotime($row["expire"]));
    }
    return date("Hi", strtotime($row["polygon_end"]));
}
function do_row($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>"
            . "<td>%02.0f</td><td>%4.2f</td><td>%s</td><td>%s</td><td>%02.0f</td></tr>",
        do_col1($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["windtag"],
        $row["hailtag"],
        $row["tornadotag"],
        $row["damagetag"],
        $row["tml_sknt"]
    );
}
function do_row_ma($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>"
            . "<td>%02.0f</td><td>%4.2f</td><td>%s</td><td>%02.0f</td></tr>",
        do_col1($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["windtag"],
        $row["hailtag"],
        $row["waterspouttag"],
        $row["tml_sknt"]
    );
}

function do_row_ffw($row)
{
    return sprintf(
        "<tr><td>%s</td><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
            "<td>%s</td></tr>",
        do_col1($row),
        $row["wfo"],
        do_col2($row),
        do_col3($row),
        $row["locations"],
        $row["floodtag_flashflood"],
        $row["floodtag_damage"],
        $row["floodtag_heavyrain"],
        $row["floodtag_dam"],
        $row["floodtag_leeve"]
    );
}

$svrtable = <<<EOF
 <table id='svr' class="table table-condensed table-striped table-bordered">
 <thead><tr><th>Eventid</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Tornado Tag</th><th>Damage Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOF;
$tortable = str_replace('svr', 'tor', $svrtable);
$smwtable = <<<EOM
 <table id='svr' class="table table-condensed table-striped table-bordered">
 <thead><tr><th>Eventid</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Waterspout Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOM;
$ffwtable = <<<EOF
 <table id='ffw' class="table table-condensed table-striped table-bordered">
 <thead><tr><th>Eventid</th><th>WFO</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Flash Flood Tag</th><th>Damage Tag</th>
 <th>Heavy Rain Tag</th><th>Dam Tag</th>
 <th>Leeve Tag</th></tr></thead>
 <tbody>
EOF;

$data = file_get_contents($jsonuri);
$json = json_decode($data, $assoc = TRUE);

foreach ($json['results'] as $key => $val) {
    if ($val["phenomena"] == 'SV') {
        $svrtable .= do_row($val);
    } elseif ($val["phenomena"] == 'TO') {
        $tortable .= do_row($val);
    } elseif ($val["phenomena"] == 'MA') {
        $smwtable .= do_row_ma($val);
    } else {
        $ffwtable .= do_row_ffw($val);
    }
}

$svrtable .= "</tbody></table>";
$tortable .= "</tbody></table>";
$ffwtable .= "</tbody></table>";
$smwtable .= "</tbody></table>";

$tselect = make_select("damagetag", $damagetag, $damagetags);

$yselect = yearSelect2(2002, $year, 'year');
$wselect = networkSelect("WFO", $wfo, array(), "wfo");
$gentime = $json["gentime"];

$t->content = <<<EOF
 <ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li>List Warning Tags Issued</li>
 </ol>
 
 <p>This application lists out Flash Flood, Marine, Severe Thunderstorm,
 and Tornado Warnings
 issued by the National Weather Service for a given year.  The listing
 includes metadata tags included in the initial warning or followup statements. 
 <strong>IMPORTANT: Not all offices include these tags in their warnings!</strong>
 For convience, this application lists out warnings back to 2002 eventhough
 these tags did not start until recent years. You should be able to copy/paste
 these tables into Microsoft Excel prior to making the table sortable!</p>
 
 <form method="GET" name="one">
 <div class="row well">
 <div class="col-sm-6">
 <input type="radio" name="opt" value="bywfo" id="bywfo" {$bywfochecked}> 
 <label for="bywfo">Select by WFO:</label> {$wselect}

 <br /> <input type="radio" name="opt" value="bydamagetag" id="bydamagetag" {$bydamagetagchecked}> 
 <label for="bydamagetag">Select by Damage Tag:</label> {$tselect}
 </div>
 <div class="col-sm-4">
 <b>Select Year:</b> {$yselect}
 </div>
 <div class="col-sm-2">
 <input type="submit" value="Generate Table">
 </div>
 </div>
 </form>
 
 <div class="alert alert-success">There is a <a href="/json/">JSON-P webservice</a>
 that provides the data found in this table.  The direct URL is:<br />
 <code>{$publicjsonuri}</code></div>
 
 <p><strong>This table is based on data generated at: {$gentime}</strong>.  There is about
 an hour worth of caching involved with this page, so please check back later for updated
 values.</p>
 
 <h3>Tornado Warnings</h3>
 <button id="create-grid2" class="btn btn-info" type="button">Make Table Sortable</button>
 {$tortable}
 
 <h3>Severe Thunderstorm Warnings</h3>
<button id="create-grid1" class="btn btn-info" type="button">Make Table Sortable</button>
         {$svrtable}

<h3>Flash Flood Warnings</h3>
<button id="create-grid3" class="btn btn-info" type="button">Make Table Sortable</button>
        {$ffwtable}

<h3>Marine Warnings</h3>
<button id="create-grid4" class="btn btn-info" type="button">Make Table Sortable</button>
        {$smwtable}

EOF;
$t->render('full.phtml');
