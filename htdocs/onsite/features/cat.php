<?php 
include("../../../config/settings.inc.php");
define("IEM_APPID", 55);
define("FBEXTRA", True); 
include("../../../include/myview.php");
$t = new MyView();

include("../../../include/database.inc.php");
include("../../../include/feature.php");
$day = isset($_GET["day"]) ? substr($_GET["day"],0,10) : null;
$offset = isset($_GET["offset"]) ? $_GET["offset"] : 0;
if ($day == null){
	$day = Date("Y-m-d");
	$offset = -1;
}

$dbconn = iemdb("mesosite");
$rs = pg_prepare($dbconn, "yesterday", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid < $1 ORDER by valid DESC limit 1");
$rs = pg_prepare($dbconn, "today", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE date(valid) = $1");
$rs = pg_prepare($dbconn, "tomorrow", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid > ($1::date + '1 day'::interval) 
              ORDER by valid ASC limit 1");

$q = "today";
if ($offset == "-1"){ $q = "yesterday"; }
else if ($offset == "+1") {$q = "tomorrow";}
$result = pg_execute($dbconn, $q, Array($day));

if (pg_num_rows($result) == 0){ die("Feature Not Found"); }

$row = pg_fetch_array($result,0);
$valid = strtotime( $row["valid"] );
$fmt = "gif";
if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }

if ($row["fbid"] == null){
	$row["fbid"] = $valid;
}

$day = $row["d"];
$thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.%s", $row["imageref"], $fmt);
$big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.%s", $row["imageref"], $fmt);

$t->title = "$day Feature - ". $row["title"]; 
$t->thispage = "iem-feature";

$content = <<<EOF
<button type="button" class="btn btn-default btn-lg">
  <span class="glyphicon glyphicon-arrow-left"></span> <a href="cat.php?day={$day}&offset=-1">Previous Feature by Date</a> 
</button>
<strong>IEM Daily Feature for {$day}</strong>
<button type="button" class="btn btn-default btn-lg">
  <a href="cat.php?day={$day}&offset=1">Next Feature by Date</a> 
  <span class="glyphicon glyphicon-arrow-right"></span> 
</button>

<!-- Begin Feature Display -->

<table cellpadding="2" cellspacing="0" border="1">
<tr><td>Title:</td><td><strong>{$row["title"]}</strong></td></tr>
<tr><td>Posted:</td><td>{$row["webdate"]}</td></tr>
</table>

<div class="row">
<div class="col-md-6">
<a href="{$big}"><img src="{$thumb}" class="img-responsive"></a>
<br /><a href="{$big}">View larger image</a>
<br />{$row["caption"]}
</div>
<div class='col-md-6 well'>{$row["story"]}
EOF;
  if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
  {
    $content .= "<br /><br /><b>Voting:</b>
    		<br />Good = ". $row["good"] 
    	." <br />Bad = ". $row["bad"] ;
    if ($row["abstain"] > 0) $content .= " <br />Abstain = ". $row["abstain"] ;
  }
  $content .= "<br />". printTags(explode(",", $row["tags"]));
$content .= <<<EOF
</div>
 		</div><!-- ./row -->
 		<div class="clearfix">&nbsp;</div>
<div class="clearfix">&nbsp;</div>
 		<div id="fb-root"></div><script src="http://connect.facebook.net/en_US/all.js#appId=196492870363354&amp;xfbml=1"></script>
<fb:comments send_notification_uid="16922938" title="{$row["title"]}" 
 href="http://mesonet.agron.iastate.edu/onsite/features/cat.php?day={$day}" 
 xid="{$row["fbid"]}" numposts="6" width="600"></fb:comments>
EOF;
$t->content = $content;
$t->render('single.phtml');
?>