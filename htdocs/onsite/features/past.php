<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | Past Features";
$ts = isset($_GET["ts"]) ? $_GET["ts"] : time();
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$THISPAGE = "iem-feature";
include("$rootpath/include/header.php"); ?>

<div class="text">
<br>List all <a href="titles.php">feature titles</a>.

<?php 
 
  if (strlen($ts) == 0) {
    echo "<p>Below you will find past daily features that appeared on the IEM 
      homepage.  The pictures are orientied to the left of the story, 
      so references to <i>above</i> are actually to the left :) </p>\n";
    $ts = date("U");
  }
  $woy = date('W', $ts);
  $yr  = date('Y', $ts);
  if ($woy == 53){
    $woy = 1;
    $yr  = "$yr or extract(year from valid) = ". (intval($yr) + 1);
  }

  $firstday = date("d M Y", $ts);

  $c = iemdb("mesosite");
  $q = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
		to_char(valid, 'Dy Mon DD, YYYY') as calhead,
		to_char(valid, 'D') as dow from feature
		WHERE extract(week from valid) = ".$woy."
                and extract(year from valid) = ".$yr."
                ORDER by valid ASC LIMIT 7";
  $rs = pg_exec($c, $q);
  pg_close($c);

  $num = pg_numrows($rs);

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold; 
	align: justify; margin: 4px; \" align=\"center\">
	<a href=\"past.php?ts=". (intval($ts) - 7 * 86400) ."\"><img src=\"/icons/back.gif\" border=0>Previous Week</a> 
	&nbsp; &nbsp; <font style=\"font-size: 16pt;\">Week of ". $firstday ."</font> &nbsp; &nbsp;
	<a href=\"past.php?ts=". (intval($ts) + 7 * 86400) ."\"><img src=\"/icons/forward.gif\" border=0>Next Week</a>
       </div>\n";
  echo "<table><tr>\n";

  for ($i = 0; $i < $num; $i++){
    $row = @pg_fetch_array($rs,$i);
    $valid = strtotime( substr($row["valid"],0,16) );

    $fmt = "gif";
    if ($valid > strtotime("2010-02-19"){ $fmt = "png"; }

    echo "<tr class=\"even\">
      <td colspan=\"2\" style=\"text-align: center;\">". $row["calhead"] ."</td></tr>
      <tr>
      <td valign=\"top\">
      <a href=\"$rooturl/onsite/features/". $row["imageref"] .".$fmt\"><img src=\"$rooturl/onsite/features/". $row["imageref"] ."_s.$fmt\" BORDER=0 ALT=\"Feature\"></a><br />".$row["caption"] ."</td>";

    echo "<td><b><a href='cat.php?day=".date("Y-m-d", $valid) ."'>". $row["title"] ."</a></b>\n";
    echo "<br><font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
    echo "<br>". $row["story"] ."";
    echo "<br>Voting: Good - ". $row["good"] ." Bad - ". $row["bad"] ;
    echo "<br />". printTags( explode(",", $row["tags"]) );
    echo "</div></td></tr>";
  }
  echo "</tr></table>\n";

  if ($num == 0){
    echo "<p>No entries found for this week\n";
  }

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold; 
        align: justify; margin: 4px; \" align=\"center\">
        <a href=\"past.php?ts=". (intval($ts) - 86400 * 7) ."\"><img src=\"/icons/back.gif\" border=0>Previous Week</a>
        &nbsp; &nbsp; <font style=\"font-size: 16pt;\">Week of ". $firstday ."</font> &nbsp; &nbsp;
        <a href=\"past.php?ts=". (intval($ts) + 86400 * 7) ."\"><img src=\"/icons/forward.gif\" border=0>Next Week</a>
       </div>\n";

?>

<BR><BR></div>

<?php include("$rootpath/include/footer.php"); ?>

