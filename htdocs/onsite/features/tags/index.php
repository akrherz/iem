<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$pgconn = iemdb('mesosite');


/* If nothing specified for a tag! */
if (! isset($_GET["tag"])){
  $rs = pg_exec($pgconn, "SELECT tags from feature WHERE tags is not Null");
  $tags = Array();
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++) { 
    $tokens = split(",", $row["tags"]);
    while (list($k,$v) = each($tokens)){ @$tags[$v] += 1; }
  }

  $THISPAGE = "iem-feature";
  $TITLE = "IEM Feature Tags";
  include("$rootpath/include/header.php");

  echo "<div style=\"padding: 15px;\">
<h3>IEM Daily Feature Tags</h3>

<p>Some of the IEM Daily Features are tagged based on the content and topic.
<br />This page summarizes the unique tags used and the number of times used.
</p>";

  echo "<table cellpadding=\"3\" cellspacing=\"0\">";
  $keys = array_keys($tags);
  asort($keys);
  $b = True;
  while (list($k,$v) = each($keys)){
    if ($b) echo "<tr>";
    echo sprintf("<td><a href=\"%s.html\">%s</a> (%s)</td>\n", $v, $v, $tags[$v]);
    if (! $b) echo "</tr>";
    $b = ! $b;
  }
  echo "</table>";
  echo "</div>";
  include("$rootpath/include/footer.php");
  die();
}

$tag = isset($_GET["tag"]) ? $_GET["tag"] : "";
$rs = pg_prepare($pgconn, "SELECT", "SELECT oid, *, 
      to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
      to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
      to_char(valid, 'YYYY-MM-DD') as permalink from feature
      WHERE tags ~* $1
      ORDER by valid DESC");
$rs = pg_execute($pgconn, "SELECT", Array($tag));

$THISPAGE = "iem-feature";
$TITLE = "IEM Features Tagged: $tag";
include("$rootpath/include/header.php");
?>
<h3>Past IEM Features tagged: <?php echo $tag; ?></h3>
<p><a href="index.php">List all tags</a></p>
<?php 

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $fmt = "gif";
  if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }
  $thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.%s", $row["imageref"], $fmt);
  $big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.%s", $row["imageref"], $fmt);
  echo "<br clear=\"all\" /><hr />";
  echo "<table>";
  echo "<tr><td>";
  echo "<img src=\"$thumb\" style=\"margin: 5px;\">";
  echo "<br /><a href=\"$big\">View larger image</a>";
  echo "<br />". $row["caption"] ;
  echo "</td><td>";
  echo "<h3><a href=\"../cat.php?day=". $row["permalink"] ."\">". $row["title"] ."</a></h3>\n";
  echo "<font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ;
  if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
  {
    echo "<br /><br /><b>Voting:</b><br />Good = ". $row["good"] ." <br />Bad =
". $row["bad"] ;
  }
  echo "<br />". printTags( explode(",", $row["tags"]) );
  echo "</div>";
  echo "</td></tr></table>";

} // End of feature for loop

if (pg_num_rows($rs) == 0)
{
  echo "<h4>No features found for this tag, sorry</h4>";
}

?>
<?php include("$rootpath/include/footer.php"); ?>
