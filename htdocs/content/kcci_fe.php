<html>
<head>
<?php
  include("../../config/settings.inc.php");
  $station = isset($_GET['station']) ? substr($_GET["station"],0,5) : 'SKCI4';
  $min = isset($_GET["min"]) ? intval($_GET["min"]) : 1;
  include("../../include/imagemaps.php");
  include("../../include/network.php");
  $nt = new NetworkTable("KCCI");
 $secs = intval($min) * 60;
?>
  <title>IEM | KCCI SchoolNet | <?php echo $nt->table[$station]["name"]; ?></title>
  <meta http-equiv="refresh" content="<?php echo $secs; ?>; URL=kcci_fe.php?min=<?php echo $min; ?>&station=<?php echo $station; ?>">

</head>
<body bgcolor="#96aae7">

<center>
<form method="POST" action="kcci_fe.php" name="st">
<?php
 
  echo "SchoolNet Site: ";
echo "<select  onChange=\"location=this.form.station.options[this.form.station.selectedIndex].value\" name=\"station\">\n";

reset($nt->table);
while( list($key, $val) = each($nt->table) ){
  echo "<option value=\"/content/kcci_fe.php?min=".$min."&station=". $key ."\"";
  if ($station == $key){
        echo " SELECTED ";
  }
  echo " >". $val["name"] ."\n";
}

echo "</select>\n";

?>
</form>
<p>
<?php
  echo "<img src=\"kcci.php?station=".$station ."\">\n";
?>

<?php if (! isset($mode) ){ ?>
<br>Refresh Every: 
<form name="refresh" action="kcci_fe.php">
<?php
  $mins = Array(1, 5, 10, 20);
  while (list($key, $val) = each($mins) ){
    echo "<input type=\"radio\" name=\"min\" value=\"". $val ."\" ";
    if ($min == $val){
      echo "CHECKED";
    }
    echo "> ". $val ." min";
  }
?>
<input type="hidden" value="<?php echo $station; ?>" name="station">
<input type="submit" value="Refresh">
</form>
<?php } ?>

</center>

</html>
