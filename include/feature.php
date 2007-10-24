<?php
  // Here is where we start pulling station Information

  $connection = iemdb("mesosite");
  $query1 = "SELECT oid, *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
                ORDER by valid DESC LIMIT 1";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);
  $foid = $row["oid"];
  $good = intval($row["good"]);
  $bad = intval($row["bad"]);
  /* Hehe, check for a IEM vote! */
  if (array_key_exists('foid', $_SESSION) && $_SESSION["foid"] == $foid)
  {

  } elseif (getenv("REMOTE_ADDR") == "129.186.142.22") 
  {

  } elseif (isset($_GET["feature_good"]))
  {
    $_SESSION["foid"] = $foid;
    $isql = "UPDATE feature SET good = good + 1 WHERE oid = $foid";
    $good += 1;
    pg_exec($connection, $isql);
  } elseif (isset($_GET["feature_bad"]))
  {
    $_SESSION["foid"] = $foid;
    $isql = "UPDATE feature SET bad = bad + 1 WHERE oid = $foid";
    $bad += 1;
    pg_exec($connection, $isql);
  }


  $fref = "/mesonet/share/features/". $row["imageref"] ."_s.gif";
  list($width, $height, $type, $attr) = @getimagesize($fref);
  $width += 2;

  $s = "<b>". $row["title"] ."</b><br />\n";
  $s .= "<div style=\"float: right; border: 1px solid #000; padding: 3px; margin: 5px; width: ${width}px;\"><a href=\"$rooturl/onsite/features/". $row["imageref"] .".gif\"><img src=\"$rooturl/onsite/features/". $row["imageref"] ."_s.gif\" alt=\"Feature\" /></a>";

  $s .= "<br />". $row["caption"] ."</div>";

  $s .= $row["webdate"] ."\n";
  $s .= "<br /><div class='story'>". $row["story"] ."</div>";
  $s .= "<br style=\"clear: right;\" /><b>Rate Feature:</b> <a href=\"$rooturl/index.phtml?feature_good\">Good</a> ($good votes) or <a href=\"$rooturl/index.phtml?feature_bad\">Bad</a> ($bad votes) &nbsp; &nbsp;<a href=\"$rooturl/onsite/features/past.php\">Past Features</a>";

/* Now, lets look for older features! */
$s .= "<br /><b>Previous Years' Features</b><table>";
$sql = "select *, extract(year from valid) as yr from feature WHERE extract(month from valid) = extract(month from now()) and extract(day from valid) = extract(day from now()) and extract(year from valid) != extract(year from now()) ORDER by yr DESC";
$result = pg_exec($connection, $sql);
for($i=0;$row=@pg_fetch_array($result,$i);$i++)
{
  if ($i % 2 == 0){ $s .= "<tr>"; }
  $s .= "<td width=\"50%\">". $row["yr"] .": <a href=\"onsite/features/cat.php?day=". substr($row["valid"], 0, 10) ."\">". $row["title"] ."</a></td>";
  if ($i % 2 != 0){ $s .= "</tr>"; }
}
$s .= "</table>";

if (getenv("REMOTE_ADDR") == "205.241.141.66" )
{
 $s = "<img src=\"images/smokey_1007.jpg\" style=\"float: left; margin: 5px;\">
Smokey, muah! <br /> &nbsp; &nbsp; &nbsp; &nbsp; 111 weeks now!!!! Smokey also a year older now, so all of the numbers are getting bigger, which is good.  I would hate for the number to go to zero and then I would be just left as 1.  That would be very sad.  I love you very much, Happy Anniversary! <br />&nbsp; &nbsp; &nbsp; &nbsp;   &nbsp; &nbsp; &nbsp; &nbsp;  love, darly";

  $s .= "<br style=\"clear: right;\" /><b>Rate Feature:</b> <a href=\"$rooturl/index.phtml?feature_good\">Good</a> ($good votes) or <a href=\"$rooturl/index.phtml?feature_bad\">Bad</a> ($bad votes) &nbsp; &nbsp;<a href=\"$rooturl/onsite/features/past.php\">Past Features</a>";
}

echo $s;
?>
