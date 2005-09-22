<?php
  $station = $_GET['station'];
  if (strlen($mode) == 0) $mode = "rt";
  if ($ostation != $station ){
    $s0 = "on";
    $s1 = "on";
    $s2 = "on";
    $s3 = "on";
    $tmpf = "on";
    $dwpf = "on";
  }

 include("/mesonet/php/lib/selectWidget.php");
 $sw = new selectWidget("/plotting/rwis/sf_fe.php", "/plotting/rwis/sf_fe.php?", "IA_RWIS");
 $swf = Array("network" => "IA_RWIS");
 $sw->setformvars($swf);
 $sw->logic($_GET);
 $swinterface = $sw->printInterface();

	include("/mesonet/php/include/header.php"); 
?>
<?php include("../../include/imagemaps.php"); ?>
<?php include("../../include/forms.php"); ?>
<b>Nav:</b> <a href="/RWIS/">RWIS</a> <b> > </b>
Pavement Temperature Time Series

<br><br>

<form method="GET" action="sf_fe.php" name="menu">
<input type="hidden" name="ostation" value="<?php echo $station; ?>">
<h2 class="heads">Site Selection:</h2>
Select from list: <?php echo rwisSelect($station); ?> or 
<a href="sf_fe.php">Select Visually</a>

<?php 
  if (strlen($station) > 0 ) { 
?>
<h2 class="heads">Plot time span:</h2>
<table width="100%">
 <tr>
   <td valign="TOP"><input type="radio" name="mode" value="rt" <?php if ($mode == "rt") echo "CHECKED"; ?>>Current</td>
   <td><input type="radio" name="mode" value="hist" <?php if ($mode == "hist") echo "CHECKED"; ?>>Historical
  <br>Start Year:<?php echo yearSelect2(2002, $syear, "syear"); ?>
  Start Month:<?php echo monthSelect2($smonth, "smonth"); ?>
  Start Day:<?php echo daySelect2($sday, "sday"); ?>
  <br>Number of days:
   <select name="days">
     <option value="1" <?php if ($days == "1") echo "SELECTED"; ?>>1
     <option value="2" <?php if ($days == "2") echo "SELECTED"; ?>>2
     <option value="3" <?php if ($days == "3") echo "SELECTED"; ?>>3
     <option value="4" <?php if ($days == "4") echo "SELECTED"; ?>>4
     <option value="5" <?php if ($days == "5") echo "SELECTED"; ?>>5
   </td>
 </tr>
</table>

<h2 class="heads">Modify Plot:</h2>
<?php

  $c0 = pg_connect('localhost', 5432, 'rwis');
  $q0 = "SELECT * from sensors WHERE station = '". $station ."' ";
  $r0 = pg_exec($c0, $q0);

  $row = @pg_fetch_array($r0, 0);
  $ns0 = $row['sensor0'];
  $ns1 = $row['sensor1'];
  $ns2 = $row['sensor2'];
  $ns3 = $row['sensor3'];

  pg_close($c0);

  $cgiStr = "&mode=$mode&sday=$sday&smonth=$smonth&syear=$syear&days=$days&";
  echo "<table width=\"100%\">
      <tr><td><b>Restrict Plot:</b>
      <br><input type=\"checkbox\" name=\"limit\" value=\"yes\" ";
  if (isset($limit)) echo "CHECKED";
  echo ">Temps between 25-35
    </td><td><b>Pavement Sensors:</b><br>\n";
  if (strlen($ns0) > 0) {
    echo "<input type=\"checkbox\" name=\"s0\" ";
    if (isset($s0)) {
      echo "CHECKED";
      $cgiStr .= "&s0=yes";
      }
    echo ">". $ns0 ."\n";
  }
  if (strlen($ns1) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s1\" ";
    if (isset($s1)) {
      echo "CHECKED";
      $cgiStr .= "&s1=yes";
    }
    echo ">". $ns1 ."\n";
  }
  if (strlen($ns2) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s2\" ";
    if (isset($s2)) {
      echo "CHECKED";
      $cgiStr .= "&s2=yes";
    }
    echo ">". $ns2 ."\n";
  }
  if (strlen($ns3) > 0) {
    echo "<br><input type=\"checkbox\" name=\"s3\" ";
    if (isset($s3)) {
      echo "CHECKED";
      $cgiStr .= "&s3=yes";
    }
    echo ">". $ns3 ."\n";
  }
  echo "</td><td><b>Other Sensors:</b><br>\n";
  echo "<input type=\"checkbox\" name=\"tmpf\" ";
  if (isset($tmpf)) {
     echo "CHECKED";
      $cgiStr .= "&tmpf=yes";
    }
  echo ">Air Temperature\n";
  echo "<br><input type=\"checkbox\" name=\"dwpf\" ";
  if (isset($dwpf)) {
     echo "CHECKED";
      $cgiStr .= "&dwpf=yes";
    }
  echo ">Dew Point\n";
  echo "<br><input type=\"checkbox\" name=\"subc\" ";
  if (isset($subc)) {
     echo "CHECKED";
      $cgiStr .= "&subc=yes";
    }
  echo ">Sub Surface\n";
  echo "</td></tr></table>";

  if (isset($limit))  $cgiStr .= "&limit=yes";

  ?>
  <input type="submit" value="Generate Plot">
  </form>

  <br><img src="SFtemps.php?station=<?php echo $station . $cgiStr; ?>" ALT="Time Series">

<?php
  } else { ?>
  
  <input type="submit" value="Generate Plot">
  </form>
  <p>This application will plot a time series of pavement 
   temperatures for a RWIS station.  Please select the RWIS station from 
   the map below.
  <?php
 echo $swinterface; 

  }
?>


<br><br>

<?php include("/mesonet/php/include/footer.php"); ?>
