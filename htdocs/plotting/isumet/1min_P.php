<?php
include("../../../config/settings.inc.php");
// 1 minute schoolnet data plotter
// Cool.....

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");


if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime( date("Y-m-d") );
}

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");


$prec = array();
$xlabel = array();
$firstPREC = 0.0;
$prevPREC = 0.0;

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $timestamp = strtotime( substr($line, 0, 26) );
  $parts = preg_split ("/\s+/", $line);
  $thisPREC = (real) ((int)($parts[10])/100.);
  $inTmpf = round (substr($line, 31, 5),2);

  if ($i == 0) {
    $firstPREC = $thisPREC;
    $prevPREC = $thisPREC;
  }

// When logger spits out bad data, the inside temperature
// is 0 degrees F.  Let's use this as a flag for poor data.
                                                                                
  if ($inTmpf <= 0.0) $thisPREC = $prevPREC;
  $prevPREC = $thisPREC;
  $thisPREC = $thisPREC - $firstPREC;

//  if ($start == 0) {
//    $start = intval($timestamp);
//  } 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;

  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
    $prec[$i] = $thisPREC;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $prec[$i] = "";
      $i++;
      $missing++;
    }
    $prec[$i] = $thisPREC;
    $i++;
    continue;
    $line_num--;
  } else if (($timestamp - $shouldbe) < 0) {
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

$max = max($prec);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
if ($max >= 0.25){
  $graph->SetScale("textlin");
  $graph->yaxis->scale->ticks->Set(1,0.05);
} else {
  $graph->SetScale("textlin",0.0,0.3);
  $graph->yaxis->scale->ticks->Set(0.05,0.01);
}
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(0.01);
$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.08);

//$graph->yaxis->scale->ticks->SetPrecision(2);

$graph->yscale->SetGrace(10);
$graph->yaxis->SetColor("blue");

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Accumulated Precipitation [inches]");
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(43);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
//$graph->SetAxisStyle(AXSTYLE_YBOXIN);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($prec);
$lineplot->SetLegend("Daily Precipitation");
$lineplot->SetColor("blue");
$lineplot->SetWeight(2);

// Box for error notations
$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
$t1->SetPos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);

$graph->Add($lineplot);
$graph->Stroke();
?>
