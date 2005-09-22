<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
        <TITLE>IEM | Past Features</TITLE>
        <META NAME="AUTHOR" CONTENT="Daryl Herzmann">
        <link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php include("../../include/header2.php"); ?>
<b>Nav:</b> <a href="/index.php">IEM Home</a> &nbsp;<b> > </b> &nbsp; Past Features
<br>List all <a href="/onsite/features/titles.php">feature titles</a>.

<?php 

  $woy1 = `date +%-W` + 1;
  if (strlen($WOY) > 0)  $woy2 = $WOY;
  else {
    echo "<p>Below you will find past daily features that appeared on the IEM 
      homepage.  The pictures are orientied to the left of the story, so references
      to <i>above</i> are actually to the left :) </p>\n";
    $woy2 = $woy1;
  }
  if ($woy2 == 53){
   $woy2 = 1;
   $woy1 = 1;
  }

  $firstday = date("d M Y", date("U") - (86400 * date("w")) - (86400 * 7 * ($woy1 - $woy2)) );
  $connection = pg_connect("10.10.10.10","5432","mesosite");
  $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
		to_char(valid, 'Dy Mon DD, YYYY') as calhead,
		to_char(valid, 'D') as dow from feature
		WHERE extract(week from valid) = ".$woy2."
                ORDER by valid ASC LIMIT 7";
  $result = pg_exec($connection, $query1);

  $num = pg_numrows($result);

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold; 
	align: justify; margin: 4px; \" align=\"center\">
	<a href=\"past.php?WOY=". (intval($woy2) - 1) ."\"><img src=\"/icons/back.gif\" border=0>Previous Week</a> 
	&nbsp; &nbsp; <font style=\"font-size: 16pt;\">Week of ". $firstday ."</font> &nbsp; &nbsp; 
	<a href=\"past.php?WOY=". (intval($woy2) + 1) ."\"><img src=\"/icons/forward.gif\" border=0>Next Week</a>
       </div>\n";
  echo "<table><tr>\n";

  for ($i = 0; $i < $num; $i++){
    $row = @pg_fetch_array($result,$i);


    echo "<tr>
      <td colspan=2 align=\"center\" bgcolor=\"#8deeee\">". $row["calhead"] ."</td></tr>
      <tr>
      <td valign=\"top\">
      <a href=\"/onsite/features/". $row["imageref"] .".gif\"><img src=\"/onsite/features/". $row["imageref"] ."_s.gif\" BORDER=0 ALT=\"Feature\"></a></td>";

    echo "<td><b>". $row["title"] ."</b>\n";
    echo "<br><font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
    echo "<br><div class='story'>". $row["story"] ."</div></td></tr>";
  }
  echo "</tr></table>\n";

  if ($num == 0){
    echo "<p>No entries found for this week\n";
  }

  echo "<div style=\"line-height: 20px; font-size: 14px; font-weight: bold; 
        align: justify; margin: 4px; \" align=\"center\">
        <a href=\"past.php?WOY=". (intval($woy2) - 1) ."\"><img src=\"/icons/back.gif\" border=0>Previous Week</a>
        &nbsp; &nbsp; <font style=\"font-size: 16pt;\">Week of ". $firstday ."</font> &nbsp; &nbsp;
        <a href=\"past.php?WOY=". (intval($woy2) + 1) ."\"><img src=\"/icons/forward.gif\" border=0>Next Week</a>
       </div>\n";

?>

<BR><BR>

<?php include("../../include/footer2.php"); ?>

