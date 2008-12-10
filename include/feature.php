<?php
  // Here is where we start pulling station Information
function printTags($tokens)
{
  global $rooturl;
  if (sizeof($tokens) == 0){ return "";}
  $s = "<br /><strong>Tags:</strong> &nbsp; ";
  while (list($k,$v) = each($tokens))
  {
    $s .= sprintf("<a href=\"%s/onsite/features/tags/%s.html\">%s</a> &nbsp; ", $rooturl, $v, $v);
  }
  return $s;
}

function genFeature()
{
  global $rooturl;

  $connection = iemdb("mesosite");
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


  $fref = "/mesonet/share/features/". $row["imageref"] ."_s.gif";
  list($width, $height, $type, $attr) = @getimagesize($fref);
  $width += 6;

  $s = "<span style=\"font-size: larger; font-weight: bold;\">". $row["title"] ."</span><br />\n";
  $s .= "<span style=\"font-size: smaller; float: left;\">Posted: " . $row["webdate"] ."</span>";
  $s .= "<span style=\"font-size: smaller; float: right;\"><a href=\"$rooturl/onsite/features/cat.php?day=". $row["permalink"] ."\">Permalink</a> | <a href=\"$rooturl/onsite/features/past.php\">Past Features</a></span>";

 /* Feature Image! */
  $s .= "<div style=\"background: #eee; float: right; border: 1px solid #ee0; padding: 3px; margin-left: 10px; width: ${width}px;\"><a href=\"$rooturl/onsite/features/". $row["imageref"] .".gif\"><img src=\"$rooturl/onsite/features/". $row["imageref"] ."_s.gif\" alt=\"Feature\" /></a><br />". $row["caption"] ."</div>";

  $s .= "<br /><div class='story' style=\"text-align: justify;\">". $row["story"] ."</div>";

/* Rate Feature and Past ones too! */
if ($row["voting"] == "f"){
  $s .= "<br clear=\"all\" />";
}
else if ($voted){
  $s .= "<br clear=\"all\" /><div style=\"float: left; margin-bottom: 10px;\">&nbsp; &nbsp;<strong> Rate Feature: </strong> Good ($good votes) or Bad ($bad votes) &nbsp; Thanks for voting!";
  $s .= printTags($tags);
  $s .= "</div>";
} else {
  $s .= "<br clear=\"all\" /><div style=\"float: left; margin-bottom: 10px;\">&nbsp; &nbsp;<strong> Rate Feature: </strong> <a href=\"$rooturl/index.phtml?feature_good\">Good</a> ($good votes) or <a href=\"$rooturl/index.phtml?feature_bad\">Bad</a> ($bad votes)";
  $s .= printTags($tags);
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



if (getenv("REMOTE_ADDR") == "173.20.163.144" )
{
 $s = "<img src=\"images/i3.jpg\" style=\"float: left; margin: 5px;\">
Smokey, muah! <br /> &nbsp; &nbsp; &nbsp; &nbsp; 169 weeks now!!!!  We get to go see the squawkeyes this weekend and darly is very excited to see smokey.  Happy Anniversary smokey.  Good thing smokey remembered it was Wednesday this morning otherwise we may have missed this week.  Darly all messed up on what day it is after playing hookie yesterday.<br />&nbsp; &nbsp; &nbsp; &nbsp;   &nbsp; &nbsp; &nbsp; &nbsp;  love, darly";

  $s .= "<br style=\"clear: right;\" /><b>Rate Feature:</b> <a href=\"$rooturl/index.phtml?feature_good\">Good</a> ($good votes) or <a href=\"$rooturl/index.phtml?feature_bad\">Bad</a> ($bad votes) &nbsp; &nbsp;<a href=\"$rooturl/onsite/features/past.php\">Past Features</a>";
}

  return $s;
}
?>
