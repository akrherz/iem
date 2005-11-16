<?php
//  1 minute data plotter 

$station = intval($station);

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('/mesonet/ARCHIVE/raw/ot/ot0006/'.$dirRef.'.dat');

$parts = array();
$maxtmp = array();
$mintmp = array();
//[DMF]$dwpf = array();
//[DMF]$sr = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 110;
$min_yaxis_i = 110;
$max_yaxis = 0;
$max_yaxis_i = 0;
$prev_Tmpf = 0.0;

while (list ($line_num, $line) = each ($fcontents)) {

  $parts = split (" ", $line);
  $month = $parts[0];
  $day = $parts[1];
  $year = $parts[2];
  $hour = $parts[3];
  $min = $parts[4];
  $thisMax = $parts[6];
  $thisMin = $parts[7];
  $timestamp = mktime($hour,$min,0,$month,$day,$year); 
  if ($thisMax < -50  ){
  } else {
    if ($max_yaxis < $thisMax){
      $max_yaxis = $thisMax;
    }
  }
                                                                                
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
 
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    $maxtmp[$i] = $thisMax;
    $mintmp[$i] = $thisMin;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc 
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $maxtmp[$i] = " ";
      $mintmp[$i] = " ";
      $xlabel[$i] ="";
      $i++;
      $missing++;
    }
    $maxtmp[$i] = $thisMax;
    $mintmp[$i] = $thisMin;
    $i++;
    continue;
    
    $line_num--;
  } else if (($timestamp - $shouldbe) < 0) {
#     echo "DUP <br>";
     $dups++;
  }

} // End of while

// Fix y[0] problems
if ($maxtmp[0] == ""){
  $maxtmp[0] = 0;
}
if ($mintmp[0] == ""){
  $mintmp[0] = 0;
}
?>

<div><font>Today's Maximum Temperature: <?php echo $thisMax; ?> F<br>
Today's Minimum Temperature: <?php echo $thisMin; ?> F<br></font></div> 
