<?php 
include("../../../config/settings.inc.php");
include("../../../include/myview.php");
include("../../../include/database.inc.php");
include("../../../include/feature.php");

$year = isset($_REQUEST["year"]) ? intval($_REQUEST["year"]) : date("Y");
$month = isset($_REQUEST["month"]) ? intval($_REQUEST["month"]) : date("m");

define("IEM_APPID", 23);
$t = new MyView();
$t->title = "Past Features";
$t->thispage = "iem-feature";

$ts = mktime(0,0,0,$month,1,$year);
$prev = $ts - 15*86400;
$plink = sprintf("past.php?year=%s&amp;month=%s", date("Y", $prev), date("m", $prev));
$next = $ts + 35*86400;
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
	ORDER by valid ASC
EOF;
$rs = pg_exec($c, $sql);

$num = pg_numrows($rs);

$linkbar = <<<EOF
<div class="row well">
	<div class="col-md-4 col-sm-4">
<a href="{$plink}" class="btn btn-default btn-lg"><i class="glyphicon glyphicon-arrow-left"></i> Previous Month</a> 
	</div>
	<div class="col-md-4 col-sm-4"><h4>Features for {$mstr}</h4></div>
	<div class="col-md-4 col-sm-4">
  <a href="{$nlink}" class="btn btn-default btn-lg">Next Month  <i class="glyphicon glyphicon-arrow-right"></i></a> 
	</div>
</div>
EOF;

for ($i = 0; $i < $num; $i++){
	$row = @pg_fetch_assoc($rs,$i);
	$valid = strtotime( substr($row["valid"],0,16) );
    $p = printTags( explode(",", $row["tags"]) );
	$fmt = "gif";
	if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }
	$d = date("Y-m-d", $valid);
    $linktext = "";
    if ($row["appurl"] != ""){
        $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"".$row["appurl"]."\"><i class=\"glyphicon glyphicon-signal\"></i> Generate This Chart on Website</a>";
    }
	
	$table .= <<<EOF
<div class="row">
  <div class="col-md-12 well well-sm">{$row["calhead"]}</large></div>
</div>

<div class="row">
	<div class="col-md-6">
	<a href="/onsite/features/{$row["imageref"]}.{$fmt}">
<img src="/onsite/features/{$row["imageref"]}.{$fmt}" alt="Feature" class="img img-responsive" /></a>
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
