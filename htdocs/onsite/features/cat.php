<?php 
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$day = $_GET["day"];
$TITLE = "IEM | Past Feature"; 
      include("$rootpath/include/header.php"); ?>
<b>Nav:</b> <a href="<?php echo $rooturl; ?>/">IEM Home</a> &nbsp;<b> > </b> &nbsp; Features


<?php 
  $day = substr($day, 0, 10);

  $connection = iemdb("mesosite");
  $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
                WHERE date(valid) = '". $day ."' ";
  $result = pg_exec($connection, $query1);
  $row = @pg_fetch_array($result,0);

  $thumb = sprintf("%s/onsite/features/%s_s.gif", $rooturl, $row["imageref"]);
  $big = sprintf("%s/onsite/features/%s.gif", $rooturl, $row["imageref"]);

  $fref = "/mesonet/share/features/". $row["imageref"] ."_s.gif";
  list($width, $height, $type, $attr) = @getimagesize($fref);
  $width += 20;

?>
<div style="width: 640px;">
<div style="float: left; width: <?php echo $width; ?>px;">
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

