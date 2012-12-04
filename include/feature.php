<?php
  // Here is where we start pulling station Information
function printTags($tokens)
{
  global $rooturl;
  if (sizeof($tokens) == 0 || $tokens[0] == ""){ return "";}
  $s = "<br /><span style=\"font-size: smaller; float: left;\">Tags: &nbsp; ";
  while (list($k,$v) = each($tokens))
  {
    $s .= sprintf("<a href=\"%s/onsite/features/tags/%s.html\">%s</a> &nbsp; ", $rooturl, $v, $v);
  }
  $s .= "</span>";
  return $s;
}

function genFeature()
{
  global $rooturl;

  $connection = iemdb("mesosite", TRUE, TRUE);
  $query1 = "SELECT oid, *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
                to_char(valid, 'YYYY-MM-DD') as permalink from feature
                ORDER by valid DESC LIMIT 1";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);
  $foid = $row["oid"];
  $good = intval($row["good"]);
  $bad = intval($row["bad"]);
  $tags = explode(",", $row["tags"]);
  $fbid = $row["fbid"];
  $fburl = "http://www.facebook.com/pages/IEM/157789644737?v=wall&story_fbid=".$fbid;
  /* Hehe, check for a IEM vote! */
  $voted = 0;
  if (array_key_exists('foid', $_COOKIE) && $_COOKIE["foid"] == $foid)
  { 
    $voted = 1;
  } elseif (getenv("REMOTE_ADDR") == "129.186.142.22" || getenv("REMOTE_ADDR") == "129.186.142.37") 
  {

  } elseif (isset($_GET["feature_good"]))
  {
    setcookie("foid", $foid, time()+100600);
    $voted = 1;

    $isql = "UPDATE feature SET good = good + 1 WHERE oid = $foid";
    $good += 1;
    pg_exec($connection, $isql);
  } elseif (isset($_GET["feature_bad"]))
  {
    setcookie("foid", $foid, time()+100600);
    $voted = 1;

    $isql = "UPDATE feature SET bad = bad + 1 WHERE oid = $foid";
    $bad += 1;
    pg_exec($connection, $isql);
  }


  $fref = "/mesonet/share/features/". $row["imageref"] ."_s.png";
  $width = 320;
  $height = 240;
  if (is_file($fref)){
	  list($width, $height, $type, $attr) = @getimagesize($fref);
  }
  $s = "<span style=\"font-size: larger; font-weight: bold;\">". $row["title"] ."</span><br />\n";
  $s .= "<span style=\"font-size: smaller; float: left;\">Posted: " . $row["webdate"] ."</span>";
  $s .= printTags($tags);

$s .= "<div style=\"font-size: smaller; float: right; margin: 5px;\">";
$s .= "<a class=\"button left\" href=\"$fburl\">Facebook</a>"; 
$s .= "<a class=\"button middle\" href=\"$rooturl/onsite/features/cat.php?day=". $row["permalink"] ."\">Permalink</a>";
$s .= "<a class=\"button middle\" href=\"$rooturl/onsite/features/past.php\">Past Features</a>";
$s .= "<a class=\"button right\" href=\"$rooturl/onsite/features/tags/\">Tags</a></div>";
  
  
 /* Feature Image! */
  $s .= "<div style=\"margin-left: 5px; border: 1px #f3f3f3 solid; float: right; padding: 3px; width: ". ($width + 6) ."px;\"><a href=\"$rooturl/onsite/features/". $row["imageref"] .".png\"><img src=\"$rooturl/onsite/features/". $row["imageref"] ."_s.png\" alt=\"Feature\" width=\"$width\" height=\"$height\"/></a><br /><span style=\"font-size: smaller;\">". $row["caption"] ."</span></div>";

  $s .= "<br /><div class='story' style=\"text-align: justify;\">". $row["story"] ."</div>";

/* Rate Feature and Past ones too! */
$s .= "<br clear=\"all\" />";
if ($row["voting"] == "f"){
  
} else {
	$s .= "<div style=\"float: left; margin-bottom: 10px; margin-left: 15px; \">";
	if ($voted){
 		$goodurl = "index.phtml";
		$badurl = "index.phtml";
		$msg = "Thanks for voting!";
	} else {
		$goodurl = "$rooturl/index.phtml?feature_good";
		$badurl = "$rooturl/index.phtml?feature_bad";
		$msg = "Rate Feature";
	}

	$s .= "<div style=\"float: left; margin-bottom: 5px;\"><strong>$msg</strong> <a class=\"button add\" href=\"$goodurl\">Good ($good votes)</a><a class=\"button delete\" href=\"$badurl\">Bad ($bad votes)</a></div>";
	$s .= "<div id=\"fb-root\"></div>";
	define("FBEXTRA", True);
	$s .= "<fb:comments send_notification_uid=\"16922938\"  title=\"". $row["title"] ."\" \" href=\"http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". $row["permalink"] ."\" xid=\"$fbid\" numposts=\"6\" width=\"520\"></fb:comments>";

	$s .= "</div>";
}
/* Now, lets look for older features! */
$s .= "<br clear=\"all\" /><strong>Previous Years' Features</strong><table width=\"100%\">";
$sql = "select *, extract(year from valid) as yr from feature WHERE extract(month from valid) = extract(month from now()) and extract(day from valid) = extract(day from now()) and extract(year from valid) != extract(year from now()) ORDER by yr DESC";
$result = pg_exec($connection, $sql);
for($i=0;$row=@pg_fetch_array($result,$i);$i++)
{
  if ($i % 2 == 0){ $s .= "<tr>"; }
  $s .= "<td width=\"50%\">". $row["yr"] .": <a href=\"onsite/features/cat.php?day=". substr($row["valid"], 0, 10) ."\">". $row["title"] ."</a></td>";
  if ($i % 2 != 0){ $s .= "</tr>"; }
}
$s .= "</table>";

  return $s;
}
?>
