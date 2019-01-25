<?php 
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 55);
define("FBEXTRA", True); 
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/feature.php";
require_once "../../../include/forms.php";

$t = new MyView();

$day = isset($_GET["day"]) ? substr(xssafe($_GET["day"]),0,10) : null;
$offset = isset($_GET["offset"]) ? intval($_GET["offset"]): 0;
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

if ($row["fbid"] == null){
	$row["fbid"] = $valid;
}

$day = $row["d"];
$prettyday = date("l, d F Y", $valid);
$big = sprintf("/onsite/features/%s.%s", $row["imageref"], $row["mediasuffix"]);

$linktext = "";
if ($row["appurl"] != ""){
	$linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"".$row["appurl"]."\"><i class=\"fa fa-signal\"></i> Generate This Chart on Website</a>";
}

$t->title = "$day Feature - ". $row["title"]; 
$t->thispage = "iem-feature";
$t->twitter_image = $big;
if ($row["mediasuffix"] == 'mp4'){
  $media = <<<EOM
  <video class="img img-responsive" controls>
	<source src="${big}" type="video/mp4">
	Your browser does not support the video tag.
</video>
EOM;
} else {
  $media = <<<EOM
<a href="{$big}"><img src="{$big}" class="img img-responsive"></a>
<br /><a href="{$big}">View larger image</a>
EOM;
}

$content = <<<EOF

<div class="row well">
	<div class="col-md-4">

<button type="button" class="btn btn-default btn-lg">
  <span class="fa fa-arrow-left"></span> <a href="cat.php?day={$day}&offset=-1">Previous Feature by Date</a> 
</button>
	</div>
	<div class="col-md-4">
<strong>IEM Daily Feature<br />{$prettyday}</strong>
	</div>
	<div class="col-md-4">
<button type="button" class="btn btn-default btn-lg">
  <a href="cat.php?day={$day}&offset=1">Next Feature by Date</a> 
  <span class="fa fa-arrow-right"></span> 
</button>
	</div>
</div>

<!-- Begin Feature Display -->

<h3>{$row["title"]}</h3>
<p><i>Posted:</i> {$row["webdate"]} </p>


<div class="row">
<div class="col-md-6">
{$media}
<br />{$row["caption"]}
{$linktext}
</div>
<div class='col-md-6 well'>{$row["story"]}
EOF;
  if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
  {
    $content .= "<br /><br /><b>Voting:</b>
    		<br />Good = ". $row["good"] 
    	." <br />Bad = ". $row["bad"]  ;
    if ($row["abstain"] > 0) $content .= " <br />Abstain = ". $row["abstain"] ;
  }
  $content .= "<br />". printTags(explode(",", $row["tags"]));

// We fouled up for a while here and was using http:// on the homepage
// and https:// here.  Rectify
$fbhttpref = "https";
if ($valid < strtotime("2016-08-09")) $fbhttpref = "http";

$content .= <<<EOF
</div>
 		</div><!-- ./row -->
 		<div class="clearfix">&nbsp;</div>
<div class="clearfix">&nbsp;</div>
 		<div id="fb-root"></div><script src="https://connect.facebook.net/en_US/all.js#appId=196492870363354&amp;xfbml=1"></script>
<fb:comments send_notification_uid="16922938" title="{$row["title"]}" 
 href="{$fbhttpref}://mesonet.agron.iastate.edu/onsite/features/cat.php?day={$day}" 
 xid="{$row["fbid"]}" numposts="6" width="600"></fb:comments>
EOF;
$t->content = $content;
$t->render('single.phtml');
?>