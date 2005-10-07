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
  if (array_key_exists('foid', $_SESSION) && intval($_SESSION["foid"]) == $foid)
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


  $fref = "/mesonet/data/features/". $row["imageref"] ."_s.gif";
  list($width, $height, $type, $attr) = getimagesize($fref);
  $width += 2;

  echo "<b>". $row["title"] ."</b><br />\n";
  echo "<div style=\"float: right; border: 1px solid #000; padding: 3px; margin: 5px; width: ${width}px;\"><a href=\"$rooturl/onsite/features/". $row["imageref"] .".gif\"><img src=\"$rooturl/onsite/features/". $row["imageref"] ."_s.gif\" alt=\"Feature\" /></a>";

  echo "<br />". $row["caption"] ."</div>";

  echo $row["webdate"] ."\n";
  echo "<br /><div class='story'>". $row["story"] ."</div>";
?>
<br style="clear: right;" /><b>Rate Feature:</b> <a href="<?php echo $rooturl; ?>/index.phtml?feature_good">Good</a> (<?php echo $good; ?> votes) or <a href="<?php echo $rooturl; ?>/index.phtml?feature_bad">Bad</a> (<?php echo $bad; ?> votes) &nbsp; &nbsp;<a href="<?php echo $rooturl; ?>/onsite/features/past.php">Past Features</a>
