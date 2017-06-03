<?php
include("../../../../config/settings.inc.php");
include("../../../../include/myview.php");
$t = new MyView();
define("IEM_APPID", 36);
include("../../../../include/database.inc.php");
include("../../../../include/feature.php");
require_once "../../../../include/forms.php";
$pgconn = iemdb('mesosite');


/* If nothing specified for a tag! */
if (! isset($_GET["tag"])){
  $rs = pg_exec($pgconn, "SELECT tags from feature WHERE tags is not Null");
  $tags = Array();
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++) { 
    $tokens = preg_split("/,/", $row["tags"]);
    while (list($k,$v) = each($tokens)){ 
		if ($v == ""){ continue; }
    	@$tags[$v] += 1; 
    }
  }

  $t->thispage = "iem-feature";
  $t->title = "Feature Tags";

  $keys = array_keys($tags);
  asort($keys);
  $b = 0;
  $table = "";
  while (list($k,$v) = each($keys)){
  	if ($b % 6 == 0) $table .= "<tr>";
  	$table .= sprintf("<td><a href=\"%s.html\">%s</a> (%s)</td>\n", $v, $v, $tags[$v]);
  	$b += 1;
  	if ($b % 6 == 0) $table .= "</tr>";
  
  }
  
  
  $t->content = <<<EOF
<h3>IEM Daily Feature Tags</h3>

<p>Some of the IEM Daily Features are tagged based on the content and topic.
<br />This page summarizes the unique tags used and the number of times used.
</p>

<table class="table table-striped table-condensed">
{$table}
</table>

EOF;
  $t->render('single.phtml');
  die();
}

$tag = isset($_GET["tag"]) ? xssafe($_GET["tag"]): "";
$t->thispage = "iem-feature";
$t->title = "Features Tagged: $tag";

$rs = pg_prepare($pgconn, "__SELECT", "SELECT oid, *, 
      to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
      to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
      to_char(valid, 'YYYY-MM-DD') as permalink from feature
      WHERE tags ~* $1
      ORDER by valid DESC");
$rs = pg_execute($pgconn, "__SELECT", Array($tag));
$content = "";
for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++)
{
	$tokens = preg_split("/,/", $row["tags"]);
	$found = False;
	while (list($k,$v) = each($tokens)){
		if ($v == $tag){ $found = True; }
	}
	if (!$found){ continue; }
	$valid = strtotime( $row["valid"] );
	$fmt = "gif";
	if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }
	$thumb = sprintf("https://mesonet.agron.iastate.edu/onsite/features/%s_s.%s", $row["imageref"], $fmt);
	$big = sprintf("https://mesonet.agron.iastate.edu/onsite/features/%s.%s", $row["imageref"], $fmt);
	$content .= <<<EOF
<hr />
<div class="row">
<div class="col-md-5">	
  <a href="$big"><img src="$big" class="img img-responsive"></a>
EOF;
	if ($row["appurl"] != ""){
		$content .= "<br /><a class=\"btn btn-sm btn-primary\" href=\"".$row["appurl"]."\"><i class=\"fa fa-signal\"></i> Generate This Chart on Website</a>";
	}
	$content .= "<br />". $row["caption"] ;
	$content .= "</div><div class=\"col-md-7\">";
	$content .= "<h3><a href=\"../cat.php?day=". $row["permalink"] ."\">". $row["title"] ."</a></h3>\n";
	$content .= "<font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
	$content .= "<br>". $row["story"] ;
	if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
	{
		$content .= "<br /><br /><b>Voting:</b><br />Good: ". $row["good"] ." <br />Bad: ". $row["bad"] ;
	}
	if (intval($row["abstain"]) > 0){
		$content .= "<br />Abstain: ". $row["abstain"];
	}
	$content .= "<br />". printTags( explode(",", $row["tags"]) );
	$content .= "</div></div>";

} // End of feature for loop

if (pg_num_rows($rs) == 0)
{
	echo "<h4>No features found for this tag, sorry</h4>";
}


$t->content = <<<EOF
<h3>Past IEM Features tagged: {$tag}</h3>
<p><a href="index.php" class="btn btn-default"><i class="fa fa-th-list"></i> List all tags</a></p>

{$content}

EOF;
$t->render('single.phtml');
?>