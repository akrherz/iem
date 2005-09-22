<table width="100%" border=0>
<tr><td colspan=2><div align="center" class="bluet">Feature of the Day:</div></td></tr>
<tr><td>
<?php
  // Here is where we start pulling station Information

  $connection = pg_connect("10.10.10.10","5432","mesosite");
  $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
                ORDER by valid DESC LIMIT 1";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);

  echo "<a href=\"/onsite/features/". $row["imageref"] .".gif\"><img src=\"/onsite/features/". $row["imageref"] ."_s.gif\" BORDER=1 ALT=\"Feature\"></a>";

  echo "<br><font style=\"color: #778899; font-size: 12pt;\">". $row["caption"] ."</font>";

  echo "</td><td>";

  echo "<b><font class='f14'>". $row["title"] ."</font></b>\n";
  echo "<br><font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ."</div>";

  echo "</td></tr></table>\n";
?>
