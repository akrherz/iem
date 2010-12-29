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
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$parts = array();
$rhf = array();
$rhi = array();
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
  $thisRhf = $parts[8];
  $thisRhi = intval($parts[18]);
  $timestamp = mktime($hour,$min,0,$month,$day,$year); 
  if ($thisRhf < 0 || $thisRhf > 100 ){
    $thisRhf = "";
  } 
  if ($thisRhi < 0 || $thisRhi > 100 ){
    $thisRhi = "";
  } 

  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;

// We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
//    echo " EQUALS <br>";
    $rhf[$i] = $thisRhf;
    $rhi[$i] = $thisRhi;
    $i++;
    continue;
  // Missed an ob, leave blank numbers, inc 
  } else if (($timestamp - $shouldbe) > 0) {
//    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $rhf[$i] = "";
      $rhi[$i] = "";
      $xlabel[$i] ="";
      $i++;
      $missing++;
    }
    $rhf[$i] = $thisRhf;
    $rhi[$i] = $thisRhi;
    $i++;
    continue;
    
    $line_num--;
  } else if (($timestamp - $shouldbe) < 0) {
//     echo "DUP <br>";
     $dups++;
  }
} // End of while

$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
        '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
        '8 PM', '9 PM', '10 PM', '11 PM', '12 AM');


for ($j=0; $j<25; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin", 0, 100);
$graph->img->SetMargin(65,40,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(10,5);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Relative Humidity");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Relative Humidity [%]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($rhf);
$lineplot->SetLegend("Outside RH");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($rhi);
$lineplot2->SetLegend("Inside RH");
$lineplot2->SetColor("red");

// Box for error notations
//[DMF]$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//[DMF]$t1->SetPos(0.4,0.95);
//[DMF]$t1->SetOrientation("h");
//[DMF]$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//[DMF]$t1->SetColor("black");
//[DMF]$graph->AddText($t1);

$graph->Add($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();

?>
