<html>
<head>
<?php
  $station = $_GET['station'];
  include('../include/kcciLoc.php');
  include("../include/imagemaps.php");
 if (strlen($station) == 0){
   $station = "SKCI4";
 }
 if (strlen($min) == 0){
   $secs = 600;
   $min = 1;
 }
 $secs = intval($min) * 60;
?>
  <title>IEM | KCCI SchoolNet | <?php echo $Scities[$station]["short"]; ?></title>
  <meta http-equiv="refresh" content="<?php echo $secs; ?>; URL=kcci_fe.php?min=<?php echo $min; ?>&station=<?php echo $station; ?>">

</head>
<body bgcolor="#96aae7">

<center>
<form method="POST" action="kcci_fe.php" name="st">
<?php
 
  echo "SchoolNet Site: ";
echo "<select  onChange=\"location=this.form.station.options[this.form.station.selectedIndex].value\" name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"/content/kcci_fe.php?min=".$min."&station=". $city["id"] ."\"";
  if ($station == $city["id"]){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."\n";
  next($Scities);
}

echo "</select>\n";

?>
</form>
<p>
<?php
  echo "<a href=\"/kcci/tool/clicktru.php?station=".$station."\" target=\"_new\"><img src=\"/kcci/spics/kcci_".$station .".gif\" border=0></a><br>\n";
  echo "<img src=\"http://mesonet.agron.iastate.edu/content/kcci.php?station=".$station ."\">\n";
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
