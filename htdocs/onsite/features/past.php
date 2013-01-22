<?php 
include("../../../config/settings.inc.php");
define("IEM_APPID", 23);
$TITLE = "IEM | Past Features";
$year = isset($_REQUEST["year"]) ? intval($_GET["year"]) : date("Y");
$month = isset($_REQUEST["month"]) ? intval($_GET["month"]) : date("m");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$THISPAGE = "iem-feature";
include("$rootpath/include/header.php"); ?>

<h3>Past Features</h3>

<p>This page lists out the IEM Daily Features for a month at a time. Features
have been posted daily since February 2002. List all 
<a href="titles.php">feature titles</a>.

<?php 
 $ts = mktime(0,0,0,$month,1,$year);
 $prev = $ts - 15*86400;
 $plink = sprintf("past.php?year=%s&month=%s", date("Y", $prev), date("m", $prev));
 $next = $ts + 35*86400; 
 $nlink = sprintf("past.php?year=%s&month=%s", date("Y", $next), date("m", $next));

 $mstr = date("M Y", $ts);
 
 $c = iemdb("mesosite");
  $q = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
		to_char(valid, 'Dy Mon DD, YYYY') as calhead,
		to_char(valid, 'D') as dow from feature
		WHERE extract(year from valid) = $year
                and extract(month from valid) = $month
                ORDER by valid ASC";
  $rs = pg_exec($c, $q);
  pg_close($c);

  $num = pg_numrows($rs);

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold; 
	align: justify; margin: 4px; \" align=\"center\">
	<a href=\"$plink\"><img src=\"/icons/back.gif\" border=0>Previous Month</a> 
	&nbsp; &nbsp; <font style=\"font-size: 16pt;\">Features for ". $mstr ."</font> &nbsp; &nbsp;
	<a href=\"$nlink\"><img src=\"/icons/forward.gif\" border=0>Next Month</a>
       </div>\n";
  echo "<table><tr>\n";

  for ($i = 0; $i < $num; $i++){
    $row = @pg_fetch_array($rs,$i);
    $valid = strtotime( substr($row["valid"],0,16) );

    $fmt = "gif";
    if ($valid > strtotime("2010-02-19")){ $fmt = "png"; }

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
    echo "<p>No entries found for this month\n";
  }

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold;
  align: justify; margin: 4px; \" align=\"center\">
  <a href=\"$plink\"><img src=\"/icons/back.gif\" border=0>Previous Month</a>
  &nbsp; &nbsp; <font style=\"font-size: 16pt;\">Features for ". $mstr ."</font> &nbsp; &nbsp;
  <a href=\"$nlink\"><img src=\"/icons/forward.gif\" border=0>Next Month</a>
  </div>\n";
  
  
?>

<?php include("$rootpath/include/footer.php"); ?>

