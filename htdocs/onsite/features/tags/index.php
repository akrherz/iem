<?php
include("../../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$pgconn = iemdb('mesosite');

$tag = isset($_GET["tag"]) ? $_GET["tag"] : "climate";

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
<?php 

for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.gif", $row["imageref"]);
  $big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.gif", $row["imageref"]);
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
