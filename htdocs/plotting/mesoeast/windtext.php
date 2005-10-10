<?php
//  1 minute data plotter 

$station = intval($station);

if (strlen($year) == 4 && strlen($month) > 0 && strlen(day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('/mesonet/ARCHIVE/raw/ot/ot0006/'.$dirRef.'.dat');

$parts = array();
$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$prev_gust = 0.0;

while (list ($line_num, $line) = each ($fcontents)) {

  $parts = split (" ", $line);
  $month = $parts[0];
  $day = $parts[1];
  $year = $parts[2];
  $hour = $parts[3];
  $min = $parts[4];
  $gust = $parts[11];
  $gust_time = $parts[12];
  $timestamp = mktime($hour,$min,0,$month,$day,$year); 
                                                                                
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
 
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    $gust = $gust;
    $gust_time = $gust_time;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc 
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $gust = "";
      $gust_time = "";
      $i++;
      $missing++;
    }
    $gust = $gust;
    $gust_time = $gust_time;
    $i++;
    continue;

    $line_num--;
  } else if (($timestamp - $shouldbe) < 0) {
#     echo "DUP <br>";
     $dups++;
  }

} // End of while

// Fix y[0] problems
if ($gust == ""){
  $gust_time = 0;
}
if ($gust_time == ""){
  $gust_time = 0;
}
?>

<div><font>Today's Maximum Wind Gust: <?php echo $gust; ?> mph<br>
Time of Maximum Wind Gust: <?php echo $gust_time; ?><br><br></font></div> 
