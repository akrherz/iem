<?php
include("$rootpath/include/mlib.php");

$myTime = strtotime($year."-".$month."-".$day);


$dirRef = strftime("%Y/%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$fcontents = file('/mnt/a1/ARCHIVE/data/'.$dirRef.'/text/ot/ot0007.dat');

/* Create data arrays */
$tmpf = array();
$dwpf = array();
$smph = array();
$drct = array();
$pmsl = array();
$rain = array();
$times = array();

$pcpn = 0;
while (list ($line_num, $line) = each ($fcontents)) {
 $tokens = split (",", $line);
 if (sizeof($tokens) != 11) continue;

 $hhmm = str_pad($tokens[3],4,"0",STR_PAD_LEFT);
 $hh = substr($hhmm,0,2);
 $mm = substr($hhmm,2,2);
 $timestamp = mktime($hh,$mm,0,$month,$day,$year);

 $times[] = $timestamp;
 $tmpf[] =  $tokens[5];
 $dwpf[] = dwpf($tokens[5], $tokens[6] );
 //$sknt[] = $tokens[7] * 1.94;
 $smph[] = $tokens[7] * 2.24;
 $drct[] = $tokens[8];
 $pmsl[] = $tokens[9];
 $pcpn += ($tokens[10] / 25.4);
 $rain[] = $pcpn;

} // End of while

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
?>

<?php
/* ------------------------- */
// Create the graph. These two calls are always required
$graph = new Graph(600,300);
$graph->SetScale("datlin");

$graph->img->SetMargin(65,40,45,60);

$graph->xaxis->SetLabelAngle(90);

$graph->title->Set("Outside Temperature");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");


$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
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

$fp = sprintf("jpg-%s-%s.png", time(), rand() );
$graph->Stroke("/var/www/htdocs/tmp/$fp");
?>
<img src="/tmp/<?php echo $fp; ?>">

<?php
/* ----------- Pressure and wind -------------- */
// Create the graph. These two calls are always required
$graph = new Graph(600,300);
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");

$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set(" Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.08);

$graph->yaxis->scale->ticks->Set(90,15);

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
$lineplot=new LinePlot($smph, $times);
$lineplot->SetLegend("Wind Speed [mph]");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($drct, $times);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

$graph->Add($sp1);
$graph->AddY2($lineplot);


$fp = sprintf("jpg-%s-%s.png", time(), rand() );
$graph->Stroke("/var/www/htdocs/tmp/$fp");
?>
<img src="/tmp/<?php echo $fp; ?>">

<?php
/* ----------- Pressure and wind -------------- */
// Create the graph. These two calls are always required
$graph = new Graph(600,300);
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");

$graph->img->SetMargin(55,45,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(0.1,0.05);
//$graph->yscale->SetGrace(10);
$graph->title->Set("Daily Precipitation");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Pressure [millibars]");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");


//[DMF]$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($rain, $times);
$lineplot->SetLegend("Precipitation");
$lineplot->SetColor("blue");

$lineplot2=new LinePlot($pmsl, $times);
$lineplot2->SetLegend("Pressure");
$lineplot2->SetColor("black");

$graph->Add($lineplot2);
$graph->AddY2($lineplot);

$fp = sprintf("jpg-%s-%s.png", time(), rand() );
$graph->Stroke("/var/www/htdocs/tmp/$fp");
?>
<img src="/tmp/<?php echo $fp; ?>">


