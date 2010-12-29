<?php
include("../../../config/settings.inc.php");
//  1 minute data plotter 

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");


if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}


$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");

$tmpf = array();
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
 
  $timestamp = strtotime( substr($line, 0, 26) );
  $thisTmpf = round (substr($line, 36, 6),2);
  $inTmpf = round (substr($line, 31, 5),2);

  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = $thisTmpf;
    }
  }

// When logger spits out bad data, the inside temperature
// is 0 degrees F.  Let's use this as a flag for poor data.
                                                                                
  if ($inTmpf <= 0.0) $thisTmpf = $prevTmpf;
  $prevTmpf = $thisTmpf;
 
  //if ($start == 0) {
  //  $start = intval($timestamp);
  //} 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
  
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    $tmpf[$i] = $thisTmpf;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $tmpf[$i] = "";
      $dwpf[$i] = "";
      $sr[$i] = "";
      $xlabel[$i] ="";
      $i++;
      $missing++;
    }
    $tmpf[$i] = $thisTmpf;
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

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
if ($min_yaxis ==  ""){
  $graph->SetScale("textlin", $min_yaxis - 4, $max_yaxis +4);
} else {
  $graph->SetScale("textlin");
}

$graph->img->SetMargin(65,40,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yaxis->scale->ticks->Set(1,0.5);
//$graph->yscale->SetGrace(10);
$graph->title->Set("Outside Temperature");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);
//[DMF]$graph->y2axis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

//[DMF]$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
//[DMF]$lineplot2=new LinePlot($dwpf);
//[DMF]$lineplot2->SetLegend("Dew Point");
//[DMF]$lineplot2->SetColor("blue");

// Create the linear plot
//[DMF]$lineplot3=new LinePlot($sr);
//[DMF]$lineplot3->SetLegend("Solar Rad");
//[DMF]$lineplot3->SetColor("black");

// Box for error notations
//[DMF]$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//[DMF]$t1->SetPos(0.4,0.95);
//[DMF]$t1->SetOrientation("h");
//[DMF]$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//[DMF]$t1->SetColor("black");
//[DMF]$graph->AddText($t1);

//[DMF]$graph->Add($lineplot2);
$graph->Add($lineplot);
//[DMF]$graph->AddY2($lineplot3);

$graph->Stroke();

?>
