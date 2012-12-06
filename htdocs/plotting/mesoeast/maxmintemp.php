<?php
//  1 minute data plotter 

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fn = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat";
$thisMax = 'Missing';
$thisMin = 'Missing';

if (file_exists($fn)){
	$fcontents = file( $fn );
	
	
	while (list ($line_num, $line) = each ($fcontents)) {
	
	  $parts = split (" ", $line);
	  $tm = $parts[6];
	  $tn = $parts[7];
	  if ($tm > $thisMax){ $thisMax = $tm; }
	  if ($tn < $thisMin){ $thisMin = $tn; }
	
	} // End of while
}	
	?>
	
	<div><font>Today's Maximum Temperature: <?php echo $thisMax; ?> F<br>
	Today's Minimum Temperature: <?php echo $thisMin; ?> F<br></font></div> 
