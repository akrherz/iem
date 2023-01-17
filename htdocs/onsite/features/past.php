<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 23);
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/feature.php";
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
$sql = <<<EOF
    SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
    to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
    to_char(valid, 'Dy Mon DD, YYYY') as calhead,
    to_char(valid, 'D') as dow from feature
    WHERE valid BETWEEN '{$year}-{$month}-01' and '{$nyear}-{$nmonth}-01'
    and valid < now() ORDER by valid ASC
EOF;
$rs = pg_exec($c, $sql);

$num = pg_num_rows($rs);

$linkbar = <<<EOF
<div class="row well">
    <div class="col-md-4 col-sm-4">
<a href="{$plink}" class="btn btn-default btn-lg"><i class="fa fa-arrow-left"></i> Previous Month</a> 
    </div>
    <div class="col-md-4 col-sm-4"><h4>Features for {$mstr}</h4></div>
    <div class="col-md-4 col-sm-4">
  <a href="{$nlink}" class="btn btn-default btn-lg">Next Month  <i class="fa fa-arrow-right"></i></a> 
    </div>
</div>
EOF;

for ($i = 0; $i < $num; $i++) {
    $row = pg_fetch_assoc($rs);
    $valid = strtotime(substr($row["valid"], 0, 16));
    $p = printTags(explode(",", is_null($row["tags"]) ? "": $row["tags"]));
    $d = date("Y-m-d", $valid);
    $linktext = "";
    if ($row["appurl"] != "") {
        $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"" . $row["appurl"] . "\"><i class=\"fa fa-signal\"></i> Generate This Chart on Website</a>";
    }
    $big = sprintf("/onsite/features/%s.%s", $row["imageref"], $row["mediasuffix"]);
    if ($row["mediasuffix"] == 'mp4') {
        $media = <<<EOM
        <video class="img img-responsive" controls>
          <source src="{$big}" type="video/mp4">
          Your browser does not support the video tag.
      </video>
EOM;
    } else {
        $media = <<<EOM
      <a href="{$big}"><img src="{$big}" class="img img-responsive"></a>
      <br /><a href="{$big}">View larger image</a>
EOM;
    }
    $table .= <<<EOF
<div class="row">
  <div class="col-md-12 well well-sm">{$row["calhead"]}</large></div>
</div>

<div class="row">
    <div class="col-md-6">
    {$media}
<br />{$row["caption"]}
    </div>
    <div class="col-md-6">

<b><a href='cat.php?day={$d}'>{$row["title"]}</a></b>
<br><font size='-1' style='color:black'>{$row["webdate"]}</font>
<br>{$row["story"]}
<br>Voting: Good - {$row["good"]} Bad - {$row["bad"]}
<br />{$p}
{$linktext}
    </div>
</div>

EOF;
}

if ($num == 0) {
    $table .= "<p>No entries found for this month\n";
}



$t->content = <<<EOF
<h3>Past Features</h3>

<p>This page lists out the IEM Daily Features for a month at a time. Features
have been posted on most days since February 2002. List all 
<a href="titles.php">feature titles</a>.

{$linkbar}
{$table}
{$linkbar}
EOF;
$t->render('single.phtml');
