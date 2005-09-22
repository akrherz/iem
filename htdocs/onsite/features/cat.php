<?php $TITLE = "IEM | Past Feature"; 
      include("/mesonet/php/include/header.php"); ?>
<b>Nav:</b> <a href="/index.php">IEM Home</a> &nbsp;<b> > </b> &nbsp; Features

<table><tr><td>

<?php 
  $day = substr($day, 0, 10);

  $connection = pg_connect("10.10.10.40","5432","mesosite");
  $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
                WHERE date(valid) = '". $day ."' ";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);

  echo "<div align=\"center\">";
  echo "<a href=\"/onsite/features/". $row["imageref"] .".gif\"><img src=\"/onsi
te/features/". $row["imageref"] ."_s.gif\" BORDER=0 ALT=\"Feature\"></a>";
  echo "<br />". $row["caption"];
  echo "</div>\n";

  echo "<b>". $row["title"] ."</b>\n";
  echo "<br><font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ."</div>";



?>

</td></tr></table>

<BR><BR>

<?php include("/mesonet/php/include/footer.php"); ?>

