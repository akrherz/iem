<?php
  // Here is where we start pulling station Information

  $connection = pg_connect("mesonet.agron.iastate.edu","5432","mesosite");
  $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
                ORDER by valid DESC LIMIT 1";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);

  echo "<div align=\"center\">";
  echo "<a href=\"/onsite/features/". $row["imageref"] .".gif\"><img src=\"/onsite/features/". $row["imageref"] ."_s.gif\" BORDER=0 ALT=\"Feature\"></a>";
  echo "</div>\n";

  echo "<b>" . $row["title"] ."</b>\n";
  echo "<br><font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ."</div>";

?>
