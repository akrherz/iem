<?php 
include("../../../config/settings.inc.php");
include("../../../include/myview.php");
$t = new MyView();
define("IEM_APPID", 23);
$t->title = "Past Features";
$year = isset($_REQUEST["year"]) ? intval($_REQUEST["year"]) : date("Y");
$month = isset($_REQUEST["month"]) ? intval($_REQUEST["month"]) : date("m");
include("../../../include/database.inc.php");
include("../../../include/feature.php");
$t->thispage = "iem-feature";

$ts = mktime(0,0,0,$month,1,$year);
$prev = $ts - 15*86400;
$plink = sprintf("past.php?year=%s&month=%s", date("Y", $prev), date("m", $prev));
$next = $ts + 35*86400;
$nlink = sprintf("past.php?year=%s&month=%s", date("Y", $next), date("m", $next));

$mstr = date("M Y", $ts);
$table = "";
$c = iemdb("mesosite");
$q = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
to_char(valid, 'Dy Mon DD, YYYY') as calhead,
to_char(valid, 'D') as dow from feature
WHERE extract(year from valid) = $year
and extract(month from valid) = $month
ORDER by valid ASC";
$rs = pg_exec($c, $q);
pg_close($c);

$num = pg_numrows($rs);

$linkbar = <<<EOF
<div class="row well">
	<div class="col-md-4 col-sm-4">
<button type="button" class="btn btn-default btn-lg">
  <span class="glyphicon glyphicon-arrow-left"></span> 
<a href="{$plink}">Previous Month</a> 
</button>
	</div>
	<div class="col-md-4 col-sm-4"><h4>Features for {$mstr}</h4></div>
	<div class="col-md-4 col-sm-4">
<button type="button" class="btn btn-default btn-lg">
  <a href="{$nlink}">Next Month</a> 
  <span class="glyphicon glyphicon-arrow-right"></span> 
</button>
	</div>
</div>
EOF;

$table .= <<<EOF
<table><tr>
EOF;
for ($i = 0; $i < $num; $i++){
	$row = @pg_fetch_assoc($rs,$i);
	$valid = strtotime( substr($row["valid"],0,16) );
    $p = printTags( explode(",", $row["tags"]) );
	$fmt = "gif";
	if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }
	$d = date("Y-m-d", $valid);
	$table .= <<<EOF
<tr class="even">
<td colspan="2" style="text-align: center;">{$row["calhead"]}</td></tr>
<tr><td valign="top">
<a href="/onsite/features/{$row["imageref"]}{$fmt}">
<img src="/onsite/features/{$row["imageref"]}_s.{$fmt}" BORDER=0 ALT="Feature"></a>
<br />{$row["caption"]}</td>
<td><b><a href='cat.php?day={$d}'>{$row["title"]}</a></b>
<br><font size='-1' style='color:black'>{$row["webdate"]}</font>
<br>{$row["story"]}
<br>Voting: Good - {$row["good"]} Bad - {$row["bad"]}
<br />{$p}
</div></td></tr>
EOF;
}
$table .= "</tr></table>\n";

if ($num == 0){
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
?>
