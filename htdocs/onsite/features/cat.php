<?php 
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$day = isset($_GET["day"]) ? substr($_GET["day"],0,10) : die("No date specified");
$offset = isset($_GET["offset"]) ? $_GET["offset"] : 0;
$TITLE = "IEM | Past Feature"; 
      include("$rootpath/include/header.php"); ?>

<h3>Past IEM Features by Date</h3>

<?php 
  $connection = iemdb("mesosite");
  $fdf = "date(valid) = '$day' ";
  if ($offset == "-1"){
    $fdf = "valid < '$day' ORDER by valid DESC limit 1";
  } else if ($offset == "+1") {
    $fdf = "date(valid) > '$day' ORDER by valid ASC limit 1";
  }
  $query1 = "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE $fdf ";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);
  $day = $row["d"];
  $thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.gif", $row["imageref"]);
  $big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.gif", $row["imageref"]);

  $fref = "/mesonet/share/features/". $row["imageref"] ."_s.gif";
  list($width, $height, $type, $attr) = @getimagesize($fref);
  $width += 20;


?>
<a href="cat.php?day=<?php echo $day; ?>&offset=-1">Previous Feature</a> &nbsp; &nbsp; <a href="cat.php?day=<?php echo $day; ?>&offset=+1">Next Feature</a>
<hr />
<div style="width: 640px;">
<div style="float: left; padding: 5px; width: <?php echo $width; ?>px;">
<img src="<?php echo $thumb; ?>" style="margin: 5px;">
<br /><a href="<?php echo $big; ?>">View larger image</a>
<br /><?php echo $row["caption"]; ?>
</div>
<?php
  echo "<h3>". $row["title"] ."</h3>\n";
  echo "<font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ;
  if (intval($row["good"]) > 0 || intval($row["bad"]) > 0)
  {
    echo "<br /><br /><b>Voting:</b><br />Good = ". $row["good"] ." <br />Bad = ". $row["bad"] ;
  }
?>
</div>


<?php include("$rootpath/include/footer.php"); ?>

