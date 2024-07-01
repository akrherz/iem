<?php
// Print out a listing of COOP sites and observation frequency
require_once "../../config/settings.inc.php";
define("IEM_APPID", 113);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
$t = new MyView();

$dbconn = iemdb("iem");

$wfo = isset($_REQUEST['wfo']) ? xssafe($_REQUEST['wfo']) : 'DMX';
$by = isset($_REQUEST['by']) ? xssafe($_REQUEST['by']) : 'station';
$tby = isset($_REQUEST['tby']) ? xssafe($_REQUEST['tby']) : 'month';
$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));

$tlabel = "month: {$month}, year: {$year}";

$tstring = sprintf("%s-%02d-01", $year, intval($month));
// sigh
if ($tby == "month") {
    if ($by == "station") {
        $rs = pg_prepare($dbconn, "MYSELECT", "select id, network, name,
        count(*) as total,
        sum(case when pday >= 0 then 1 else 0 end) as pobs, 
        sum(case when snow >= 0 then 1 else 0 end) as sobs, 
        sum(case when snowd >= 0 then 1 else 0 end) as sdobs, 
        sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
        from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
        WHERE day >= $1 and day < ($1::date + '1 month'::interval) 
        and day < 'TOMORROW'::date
        and t.wfo = $2 and t.network ~* 'COOP' GROUP by id, network, name
        ORDER by id ASC");
    } else {
        $rs = pg_prepare($dbconn, "MYSELECT", "select day,
     count(*) as total,
     sum(case when pday >= 0 then 1 else 0 end) as pobs, 
     sum(case when snow >= 0 then 1 else 0 end) as sobs, 
     sum(case when snowd >= 0 then 1 else 0 end) as sdobs, 
     sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
     from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
     WHERE day >= $1 and day < ($1::date + '1 month'::interval) 
     and day < 'TOMORROW'::date
     and t.wfo = $2 and t.network ~* 'COOP' GROUP by day ORDER by day ASC");
    }
    $args = array($tstring, $wfo);
} else {
    $tlabel = "year: {$year}";
    if ($by == "station") {
        $rs = pg_prepare($dbconn, "MYSELECT", "select id, network, name,
        count(*) as total,
        sum(case when pday >= 0 then 1 else 0 end) as pobs, 
        sum(case when snow >= 0 then 1 else 0 end) as sobs, 
        sum(case when snowd >= 0 then 1 else 0 end) as sdobs, 
        sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
        from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
        WHERE day < 'TOMORROW'::date
        and t.wfo = $1 and t.network ~* 'COOP' GROUP by id, network, name
        ORDER by id ASC");
    } else {
        $rs = pg_prepare($dbconn, "MYSELECT", "select day,
     count(*) as total,
     sum(case when pday >= 0 then 1 else 0 end) as pobs, 
     sum(case when snow >= 0 then 1 else 0 end) as sobs, 
     sum(case when snowd >= 0 then 1 else 0 end) as sdobs, 
     sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
     from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
     WHERE day < 'TOMORROW'::date
     and t.wfo = $1 and t.network ~* 'COOP' GROUP by day ORDER by day ASC");
    }
    $args = array($wfo);
}

$bselect = make_select("by", $by, array("station" => "Station", "day" => "Day"));
$tselect = make_select("tby", $tby, array("month" => "Month", "year" => "Year"));

$data = pg_execute($dbconn, "MYSELECT", $args);

$t->title = "NWS COOP Obs per month per WFO";

$wselect = networkSelect("WFO", $wfo, array(), "wfo");

$ys = yearSelect("2010", $year);
$ms = monthSelect($month);

$table = "";
for ($i = 0; $row = pg_fetch_assoc($data); $i++) {
    if ($by == "station") {
        $table .= sprintf(
            "<tr><td><a href=\"/sites/site.php?station=%s&amp;network=%s\">%s</a></td>" .
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
                "<td>%s</td><td>%s</td></tr>",
            $row["id"],
            $row["network"],
            $row["id"],
            $row["name"],
            $row["total"],
            $row["pobs"],
            $row["tobs"],
            $row["sobs"],
            $row["sdobs"]
        );
    } else {
        $table .= sprintf(
            "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" .
                "<td>%s</td></tr>",
            $row["day"],
            $row["total"],
            $row["pobs"],
            $row["tobs"],
            $row["sobs"],
            $row["sdobs"]
        );
    }
}
$header = "<th>NWSLI</th><th>Name</th>";
if ($by == "day") {
    $header = "<th>Day</th>";
}

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="active">NWS COOP Observation Counts by Month by WFO</li>
</ol>

<p>This application prints out a summary of COOP reports received by the IEM 
on a per month and per WFO basis.  Errors do occur and perhaps the IEM's ingestor
is "missing" data from sites.  Please <a href="/info/contacts.php">let us know</a> of any errors you may suspect!

<form method="GET" name="changeme">
<table class="table table-condensed">
<tr>
<td><strong>Select WFO:</strong> {$wselect} </td>
<td><strong>Aggregate By:</strong> {$bselect} </td>
<td><strong>By Month or Year:</strong> {$tselect} </td>
<td><strong>Select Year:</strong>{$ys}</td>
<td><strong>Select Month:</strong>{$ms}</td>
</tr>
</table>
<input type="submit" value="View Report" />
</form>

<h3>COOP Report for wfo: {$wfo}, {$tlabel}</h3>

<table class="table table-striped table-condensed table-bordered">
<thead class="sticky">
<tr>{$header}<th>Possible</th>
<th>Precip Obs</th><th>Temperature Obs</th><th>Snowfall Obs</th>
<th>Snowdepth Obs</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
EOF;
$t->render('full.phtml');
