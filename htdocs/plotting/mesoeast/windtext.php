<?php
//  1 minute data plotter 


$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$maxGust = 0;
$gustTime = 0;

while (list ($line_num, $line) = each ($fcontents)) {

  $parts = split (" ", $line);
  $gust = $parts[11];
  $gust_time = $parts[12];
  if ($gust > $maxGust){ $maxGust = $gust; $gustTime = $gust_time;}
} // End of while

?>

<div><font>Today's Maximum Wind Gust: <?php echo $maxGust; ?> mph<br>
Time of Maximum Wind Gust: <?php echo $gustTime; ?><br><br></font></div> 
