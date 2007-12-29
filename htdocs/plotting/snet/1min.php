<?php
// 1 minute schoolnet data plotter
// Cool.....
// 16 Sep 2002:	Account for bad RH data
//  4 Dec 2002:	Account for those negative temps
// 18 Dec 2003	We need to do some tricks to account for sites with very
//		little reporting (temporally)
//  3 Apr 2005  What the heck am I doing?

include ("../../include/snet_locs.php");
include ("fillholes.inc.php");

$network = $_GET["network"];
$sid = isset( $_GET["station"] ) ? $_GET["station"]: 'SKCI4';
$station = $cities[$network][$station]["nwn_id"];

//echo "HELLO:$station:HELLO";
$year = isset( $_GET["year"] ) ? $_GET["year"] : date("%Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("%m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("%d");

$myTime = strtotime($year."-".$month."-".$day);
$dirRef = strftime("%Y_%m/%d", $myTime);
$matchDate = strftime("%m/%d/%y", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);
$fcontents = file('/mesonet/ARCHIVE/raw/snet/'.$dirRef.'/'.$station.'.dat');

$tmpf = array();
$dwpf = array();
$sr = array();
$xlabel = array();
for ($i=0;$i<=1440;$i++)
{
  $tmpf[$i] = " ";
  $dwpf[$i] = " ";
  $sr[$i] = " ";
}

$start = intval( $myTime );
$i = 0;

$min_yaxis = 100;
$max_yaxis = 0;

while (list ($line_num, $line) = each ($fcontents)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];
  $thisDate = $parts[1];
  if ($thisDate != $matchDate) continue;

  $hhmm = split (":", $thisTime);
  $offset = intval($hhmm[0]) * 60 + intval($hhmm[1]);

  if (substr($parts[6], 0, 2) == "0-"){
    $thisTmpf = intval( substr($parts[6], 1, 2) ) ;
  } else {
    $thisTmpf = intval( substr($parts[6], 0, 3) ) ;
  }
  $thisRelH = intval( substr($parts[7],0,3) );
  $thisSR = intval( substr($parts[4],0,3) ) * 10;

  if ($thisRelH > 0){
    $thisTmpk = 273.15 + (5.00/9.00 * ($thisTmpf - 32.00 ));
    $thisDwpk = $thisTmpk / (1+ 0.000425 * $thisTmpk * -(log10($thisRelH/100.00)));
    $thisDwpf = intval( ( $thisDwpk - 273.15 ) * 9.00/5.00 + 32 );
  } else {
    $thisDwpf = " ";
  }

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

  $tmpf[$offset] = $thisTmpf;
  $dwpf[$offset] = $thisDwpf;
  $sr[$offset] = $thisSR;

} // End of while

$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
        '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
        '8 PM', '9 PM', '10 PM', '11 PM', 'Midnight');


for ($j=0; $j<25; $j++){
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

$tmpf = fillholes($tmpf);
$dwpf = fillholes($dwpf);
$sr = fillholes($sr);

include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
if ($min_yaxis ==  ""){
  $graph->SetScale("textlin", $min_yaxis - 4, $max_yaxis +4);
} else {
  $graph->SetScale("textlin");
}
$graph->SetY2Scale("lin", 0, 1200);
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
$graph->legend->Pos(0.01,0.075);

$graph->y2axis->scale->ticks->Set(100,25);
$graph->y2axis->scale->ticks->SetPrecision(0);
$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);

$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time  ");
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
//$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//$t1->SetPos(0.4,0.95);
//$t1->SetOrientation("h");
//$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//$t1->SetColor("black");
//$graph->AddText($t1);

$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke();

?>
