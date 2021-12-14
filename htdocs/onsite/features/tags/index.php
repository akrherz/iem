<?php
require_once "../../../../config/settings.inc.php";
require_once "../../../../include/myview.php";
$t = new MyView();
define("IEM_APPID", 36);
require_once "../../../../include/database.inc.php";
require_once "../../../../include/feature.php";
require_once "../../../../include/forms.php";
$pgconn = iemdb('mesosite');


/* If nothing specified for a tag! */
if (! isset($_GET["tag"])){
  $rs = pg_exec($pgconn, "SELECT tags from feature WHERE tags is not Null");
  $tags = Array();
  for ($i=0;$row=pg_fetch_array($rs);$i++) { 
    $tokens = preg_split("/,/", $row["tags"]);
    foreach($tokens as $k => $v)
    { 
		if ($v == ""){ continue; }
    	@$tags[$v] += 1; 
    }
  }

  $t->title = "Feature Tags";

  $keys = array_keys($tags);
  asort($keys);
  $b = 0;
  $table = "";
  foreach($keys as $k => $v)
  {
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
$t->title = "Features Tagged: $tag";

$winterextra = "";
if (strpos($tag, "winter") === 0){
	$winterextra = <<<EOM
<p>The IEM generates per winter storm analyses of snowfall reports over
Iowa and tags them by the winter season.  Here are the tags used for the
previous winter seasons that these maps are available for:
<ul>
	<li><a href="winter1011.html">Winter 2010-2011</a></li>
	<li><a href="winter1112.html">Winter 2011-2012</a></li>
	<li><a href="winter1213.html">Winter 2012-2013</a></li>
	<li><a href="winter1314.html">Winter 2013-2014</a></li>
	<li><a href="winter1415.html">Winter 2014-2015</a></li>
	<li><a href="winter1516.html">Winter 2015-2016</a></li>
	<li><a href="winter1617.html">Winter 2016-2017</a></li>
	<li><a href="winter1718.html">Winter 2017-2018</a></li>
	<li><a href="winter1819.html">Winter 2018-2019</a></li>
	<li><a href="winter1920.html">Winter 2019-2020</a></li>
	<li><a href="winter2021.html">Winter 2020-2021</a></li>
	<li><a href="winter2122.html">Winter 2021-2022</a></li>
</ul></p>

EOM;
}

$rs = pg_prepare($pgconn, "__SELECT", "SELECT *, 
      to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
      to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
      to_char(valid, 'YYYY-MM-DD') as permalink from feature
      WHERE tags ~* $1
      ORDER by valid DESC");
$rs = pg_execute($pgconn, "__SELECT", Array($tag));
$content = "";
for ($i=0;$row=pg_fetch_assoc($rs);$i++)
{
	$tokens = preg_split("/,/", $row["tags"]);
	$found = False;
    foreach($tokens as $k => $v)
    {
		if ($v == $tag){ $found = True; }
	}
	if (!$found){ continue; }
	$valid = strtotime( $row["valid"] );
	$big = sprintf("/onsite/features/%s.%s", $row["imageref"], $row["mediasuffix"]);
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
	$content .= <<<EOF
<hr />
<div class="row">
<div class="col-md-5">	
	  {$media}
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

{$winterextra}

{$content}

EOF;
$t->render('single.phtml');
?>