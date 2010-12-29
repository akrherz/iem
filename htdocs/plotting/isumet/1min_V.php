<?php
include("../../../config/settings.inc.php");
// 1 minute schoolnet data plotter
// 18 Sep 2002 - Denote when the averaging scheme happened!
//  3 Dec 2002 - Make sure that scale of wind axis is okay!

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime( date("Y-m-d") );
}

$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min Instantaneous Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");


$mph = array();
$drct = array();
$gust = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$hasgust = 0;
$peakGust = 0;
$peaksped = 0;
$prevMPH = 0;
$prevDRCT = 0;

while (list ($line_num, $line) = each ($fcontents)) {

  $timestamp = strtotime( substr($line, 0, 26) );
  $parts = preg_split ("/\s+/", $line);
  $inTmpf = round (substr($line, 31, 5),2);
//  $thisMPH = intval( substr($parts[11],0,-3) );
  $thisMPH = intval($parts[8]);
  if ($thisMPH > $peaksped) $peaksped = $thisMPH;
  $thisDRCT = intval($parts[9]);

// When logger spits out bad data, the inside temperature
// is 0 degrees F.  Let's use this as a flag for poor data.
                                                                                
  if ($inTmpf <= 0.0){
    $thisMPH = $prevMPH;
    $thisDRCT = $prevDRCT;
  }
  $prevMPH = $thisMPH;
  $PrevDRCT = $thisDRCT;

# Add quality control

//  if ($start == 0) {
//    $start = intval($timestamp);
//  } 
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
  
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    if ($i % 5 == 0){
      $drct[$i] = $thisDRCT;
    }else{
      $drct[$i] = "-199";
    }
    $mph[$i] = $thisMPH;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $drct[$i] = "-199";
      $mph[$i] = "";

      $i++;
      $missing++;
    }
    if ($i % 5 == 0){
      $drct[$i] = $thisDRCT;
    } else {
      $drct[$i] = "-199";
    }
    $mph[$i] = $thisMPH;
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

if ($peaksped > $peakGust) $peakGust = $peaksped;

for ($j=0; $j<24; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin",0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.08);

$graph->yaxis->scale->ticks->Set(90,15);
//$graph->yaxis->scale->ticks->SetPrecision(0);
//$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);

$graph->yaxis->SetTitle("Wind Direction");
$graph->y2axis->SetTitle("Wind Speed [MPH]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($mph);
$lineplot->SetLegend($wLabel);
$lineplot->SetColor("red");

if ($hasgust == 1){
  // Create the linear plot
  $lp1=new LinePlot($gust);
  $lp1->SetLegend("Peak Wind Gust");
  $lp1->SetColor("black");
}

// Create the linear plot
$sp1=new ScatterPlot($drct);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

// Box for error notations
$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
$t1->SetPos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);


$graph->Add($sp1);
$graph->AddY2($lineplot);
if ($hasgust == 1){
  $graph->AddY2($lp1);
}
$graph->Stroke();
?>
