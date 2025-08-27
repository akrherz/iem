<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 23);
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/mlib.php";
require_once "../../../include/forms.php";

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));

$t = new MyView();
$t->title = "Past Features";

$ts = mktime(0, 0, 0, $month, 1, $year);
$prev = $ts - 15 * 86400;
$plink = sprintf("past.php?year=%s&amp;month=%s", date("Y", $prev), date("m", $prev));
$next = $ts + 35 * 86400;
$nmonth = date("m", $next);
$nyear = date("Y", $next);
$nlink = sprintf("past.php?year=%s&amp;month=%s", $nyear, $nmonth);

$mstr = date("M Y", $ts);
$table = "";
$c = iemdb("mesosite");
$sql = <<<EOM
    SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
    to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
    to_char(valid, 'Dy Mon DD, YYYY') as calhead,
    to_char(valid, 'D') as dow from feature
    WHERE valid BETWEEN $1 and $2
    and valid < now() ORDER by valid ASC
EOM;
$stname = iem_pg_prepare($c, $sql);
$rs = pg_execute($c, $stname, Array("{$year}-{$month}-01", "{$nyear}-{$nmonth}-01"));

$num = pg_num_rows($rs);

$linkbar = <<<EOM
<nav class="d-flex justify-content-between align-items-center mb-3" aria-label="Month navigation">
    <div>
        <a href="{$plink}" class="btn btn-outline-secondary btn-sm" aria-label="Previous month">&larr; Previous</a>
    </div>
    <div class="text-center flex-fill">
        <h4 class="mb-0" aria-live="polite">Features for {$mstr}</h4>
    </div>
    <div class="text-end">
        <a href="{$nlink}" class="btn btn-outline-secondary btn-sm" aria-label="Next month">Next &rarr;</a>
    </div>
</nav>
EOM;

while ($row = pg_fetch_assoc($rs)) {
    $valid = strtotime(substr($row["valid"], 0, 16));
    $iso = date('c', $valid);
    $alt = htmlspecialchars($row["title"], ENT_QUOTES);
    $p = printTags(explode(",", is_null($row["tags"]) ? "": $row["tags"]));
    $d = date("Y-m-d", $valid);
    $linktext = "";
    if ($row["appurl"] != "") {
        $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"" . $row["appurl"] . "\"><i class=\"bi bi-signal\" aria-hidden=\"true\"></i> Generate This Chart on Website</a>";
    }
        $big = sprintf("/onsite/features/%s.%s", $row["imageref"], $row["mediasuffix"]);
        if ($row["mediasuffix"] == 'mp4') {
                $media = <<<EOM
                <figure class="figure">
                    <video class="img-fluid" controls aria-label="Feature video for {$alt}">
                        <source src="{$big}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <figcaption class="figure-caption small">{$row["caption"]}</figcaption>
                </figure>
EOM;
        } else {
                $media = <<<EOM
                <figure class="figure">
                    <a href="{$big}"><img src="{$big}" class="img-fluid rounded" alt="{$alt}"></a>
                    <figcaption class="figure-caption small"><a href="{$big}">View larger image</a> — {$row["caption"]}</figcaption>
                </figure>
EOM;
        }

        $table .= <<<EOM
<article class="mb-4">
    <div class="card">
        <div class="card-body p-2">
            <h5 class="mb-0">{$row["calhead"]}</h5>
        </div>
    </div>

    <div class="row mt-2">
        <div class="col-12 col-md-6"> 
            {$media}
        </div>
        <div class="col-12 col-md-6">
            <h3 id="feature-title-{$d}" class="h5"><a href='cat.php?day={$d}'>{$row["title"]}</a></h3>
            <p class="mb-1"><small class="text-muted"><time datetime="{$iso}">{$row["webdate"]}</time></small></p>
            <div>{$row["story"]}</div>
            <p class="mt-2 mb-1">Voting: <span class="me-2">Good - {$row["good"]}</span> <span>Bad - {$row["bad"]}</span></p>
            <div>{$p}</div>
            <div class="mt-2">{$linktext}</div>
        </div>
    </div>
</article>

EOM;
}

if ($num == 0) {
    $table .= "<p>No entries found for this month\n";
}

$t->content = <<<EOM
<h3>Past Features</h3>

<p>This page lists out the IEM Daily Features for a month at a time. Features
have been posted on most days since February 2002. List all 
<a href="titles.php">feature titles</a>.

{$linkbar}
{$table}
{$linkbar}
EOM;
$t->render('single.phtml');
