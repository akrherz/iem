<?php
require_once "../../../config/settings.inc.php";
//  1 minute data plotter 
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

function dwpf($tmpf, $relh){
  $tmpk = 273.15 + (5.00/9.00 * ($tmpf - 32.00));
  $dwpk = $tmpk / (1 + 0.000425 * $tmpk * - (log10($relh/100)));
  return round( ($dwpk - 273.15) * 9.00/5.00 + 32,2 );
}

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");

$formatFloor = mktime(0, 0, 0, 1, 1, 2016);
if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);

$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0006.dat");

$parts = array();
$tmpf = array();
$dwpf = array();
$xlabel = array();
$times = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 110;
$min_yaxis_i = 110;
$max_yaxis = 0;
$max_yaxis_i = 0;
$prev_Tmpf = 0.0;

foreach($fcontents as $line_num => $line){
    $parts = explode(" ", $line);
    $times[] = strtotime(sprintf("%s %s %s %s %s", $parts[0], $parts[1],
            $parts[2], $parts[3], $parts[4]));
  $thisTmpf = $parts[17];
  $thisrh = $parts[18];
  $thisDwpf = dwpf($thisTmpf,$thisrh);
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = ceil($thisTmpf);
    }
    if ($min_yaxis > $thisDwpf){
      $min_yaxis = floor($thisDwpf);
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = "";
  } else {
    if ($max_yaxis < $thisDwpf){
      $max_yaxis = ceil($thisDwpf);
    }
    if ($min_yaxis > $thisDwpf){
      $min_yaxis = floor($thisDwpf);
    }
  }


    $tmpf[] = $thisTmpf;
    $dwpf[] = $thisDwpf;
 
} // End of while


// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datelin");

$graph->img->SetMargin(65,40,45,80);
$graph->xaxis->SetLabelFormatString("h:i A", true);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(2,1);
$graph->yaxis->scale->SetGrace(10);
$graph->title->Set("Inside Temperatures");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

$graph->Add($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();
