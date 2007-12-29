<?php
// 1 minute schoolnet data plotter
// Cool.....

include ("../../include/snet_locs.php");

if (strlen($station) > 3){
    $station = $SconvBack[$station];
}

$station = intval($station);


if (strlen($year) == 4 && strlen($month) > 0 && strlen(day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}


$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('/mesonet/ARCHIVE/raw/snet/'.$dirRef.'/'.$station.'.dat');

$tmpf = array();
$dwpf = array();
$sr = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 100;
$max_yaxis = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];
  $thisDate = $parts[1];
  $dateTokens = split("/", $thisDate);
  $strDate = "20". $dateTokens[2] ."-". $dateTokens[0] ."-". $dateTokens[1]; 
  $timestamp = strtotime($strDate ." ". $thisTime );
#  echo $thisTime ."||";
  
  $thisTmpf = intval( substr($parts[6],0,3) );
  $thisRelH = intval( substr($parts[7],0,3) );
  $thisSR = intval( substr($parts[4],0,3) ) * 10;
  $thisTmpk = 273.15 + (5.00/9.00 * ($thisTmpf - 32.00 ));
  $thisDwpk = $thisTmpk / (1+ 0.000425 * $thisTmpk * -(log10($thisRelH/100.00)));
  $thisDwpf = intval( ( $thisDwpk - 273.15 ) * 9.00/5.00 + 32 );
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = " ";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = $thisTmpf;
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = " ";
  }  else {
    if ($min_yaxis > $thisDwpf){
      $min_yaxis = $thisDwpf;
    }
  }

 
  //if ($start == 0) {
  //  $start = intval($timestamp);
  //} 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
  
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    $tmpf[$i] = $thisTmpf;
    $dwpf[$i] = $thisDwpf;
    $sr[$i] = $thisSR;
    $xlabel[$i] = $thisTime;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $tmpf[$i] = " ";
      $dwpf[$i] = " ";
      $sr[$i] = " ";
      $xlabel[$i] ="";
      $i++;
      $missing++;
    }
    $tmpf[$i] = $thisTmpf;
    $dwpf[$i] = $thisDwpf;
    $sr[$i] = $thisSR;
    $xlabel[$i] = $thisTime;
    $i++;
    continue;
    
    $line_num--;
  } else if (($timestamp - $shouldbe) < 0) {
#    echo "DUP <br>";
     $dups++;
    
  }

} // End of while

$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
        '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
        '8 PM', '9 PM', '10 PM', '11 PM', 'Midnight');


for ($j=0; $j<24; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


// Fix y[0] problems
if ($tmpf[0] == ""){
  $tmpf[0] = 0;
}
if ($dwpf[0] == ""){
  $dwpf[0] = 0;
}
if ($sr[0] == ""){
  $sr[0] = 0;
}



include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin", $min_yaxis - 4, $max_yaxis +4);
//$graph->SetY2Scale("lin", 0, 900);
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yscale->SetGrace(10);
$graph->title->Set($Scities[$Sconv[$station]]['city'] ." Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.09);

$graph->yaxis->scale->ticks->Set(5,1);
//$graph->y2axis->scale->ticks->SetPrecision(0);
$graph->yaxis->scale->ticks->SetPrecision(0);


$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Temperature [F]");
//$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($dwpf);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($sr);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");

// Box for error notations
$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
$t1->SetPos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);

$graph->Add($lineplot2);
$graph->Add($lineplot);
#$graph->AddY2($lineplot3);

$graph->Stroke();

?>
