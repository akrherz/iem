<?php
$conn = iemdb("mesosite");
$rs = pg_exec($conn, "SELECT * from news ORDER by entered DESC LIMIT 5");
pg_close($conn);

$today = mktime(0,0,0, date("m"), date("d"), date("Y"));

for ($i=0; $row = @pg_fetch_array($rs, $i); $i++){
  $ts = strtotime(substr($row["entered"],0,16));
  if ($ts > $today) $sts = strftime("%I:%M %p", $ts);
  else $sts = strftime("%d %b %I:%M %p", $ts);
  echo "<a href=\"$rooturl/onsite/news.phtml?id=".$row["id"]."\">". $row["title"] ."</a><div class=\"iem-news-descript\"><i>Posted:</i> $sts</div>\n";
}
?>
