<?php
// Print out a listing of COOP sites and observation frequency
require_once "../../config/settings.inc.php";
define("IEM_APPID", 113);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$t = new MyView();

$dbconn = iemdb("iem");

$wfo = get_str404('wfo', 'DMX');
$by = get_str404('by', 'station');
$tby = get_str404('tby', 'month');
$dt = dt_from_cgi_ymd();
$year = intval($dt->format("Y"));
$month = intval($dt->format("m"));
$tlabel = "month: {$month}, year: {$year}";

$tstring = sprintf("%s-%02d-01", $year, intval($month));
// sigh
if ($tby == "month") {
    if ($by == "station") {
        $stname = iem_pg_prepare($dbconn, "select id, network, name,
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
        $stname = iem_pg_prepare($dbconn, "select day,
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
        $stname = iem_pg_prepare($dbconn, "select id, network, name,
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
        $stname = iem_pg_prepare($dbconn, "select day,
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

$bselect = make_select(
    "by",
    $by,
    array("station" => "Station", "day" => "Day"),
    "",
    "form-select",
    FALSE,
    FALSE,
    TRUE,
    array("id" => "by"),
);
$tselect = make_select(
    "tby",
    $tby,
    array("month" => "Month", "year" => "Year"),
    "",
    "form-select",
    FALSE,
    FALSE,
    TRUE,
    array("id" => "tby"),
);

$data = pg_execute($dbconn, $stname, $args);

$t->title = "NWS COOP Obs per month per WFO";

$wselect = networkSelect("WFO", $wfo, array(), "wfo", FALSE, "form-select");
$addSelectAttributes = function ($select, $id) {
    $select = str_replace('class="iemselect2"', 'class="form-select iemselect2"', $select);
    if (strpos($select, 'class="') === false) {
        $select = str_replace("<select ", '<select class="form-select" ', $select);
    }
    return str_replace("<select ", "<select id=\"{$id}\" ", $select);
};
$wselect = $addSelectAttributes($wselect, "wfo");

$ys = $addSelectAttributes(yearSelect("2010", $year), "year");
$ms = $addSelectAttributes(monthSelect($month), "month");

$table = "";
while ($row = pg_fetch_assoc($data)) {
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
$header = "<th scope=\"col\">NWSLI</th><th scope=\"col\">Name</th>";
if ($by == "day") {
    $header = "<th scope=\"col\">Day</th>";
}

$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb mb-3">
 <li class="breadcrumb-item"><a href="/nws/">NWS User Resources</a></li>
 <li class="breadcrumb-item active" aria-current="page">NWS COOP Observation Counts by Month by WFO</li>
</ol>
</nav>

<header class="mb-4">
<h1 class="h3">NWS COOP Observation Counts</h1>
<p class="mb-0">This application prints out a summary of COOP reports received by the IEM
on a per month and per WFO basis.  Errors do occur and perhaps the IEM's ingestor
is "missing" data from sites. Please <a href="/info/contacts.php">let us know</a> of any errors you may suspect.</p>
</header>

<form method="GET" name="changeme" class="card shadow-sm mb-4">
<div class="card-body">
<div class="row g-3 align-items-end">
<div class="col-md-6 col-lg-3">
<label for="wfo" class="form-label">WFO</label>
{$wselect}
</div>
<div class="col-sm-6 col-lg-2">
<label for="by" class="form-label">Aggregate by</label>
{$bselect}
</div>
<div class="col-sm-6 col-lg-2">
<label for="tby" class="form-label">Time period</label>
{$tselect}
</div>
<div class="col-sm-6 col-lg-2">
<label for="year" class="form-label">Year</label>
{$ys}
</div>
<div class="col-sm-6 col-lg-2">
<label for="month" class="form-label">Month</label>
{$ms}
</div>
<div class="col-lg-1">
<button type="submit" class="btn btn-primary w-100">View</button>
</div>
</div>
</div>
</form>

<section aria-labelledby="report-heading">
<h2 id="report-heading" class="h5">COOP report for WFO {$wfo}, {$tlabel}</h2>

<div class="table-responsive">
<table class="table table-striped table-sm table-bordered table-hover align-middle">
<thead class="sticky">
<tr>{$header}<th scope="col">Possible</th>
<th scope="col">Precip Obs</th><th scope="col">Temperature Obs</th><th scope="col">Snowfall Obs</th>
<th scope="col">Snowdepth Obs</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>
</section>
EOM;
$t->render('full.phtml');
