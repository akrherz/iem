<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$df = Array();
$df_times = Array();
$fcontents = file('freezer.dat');
while (list ($line_num, $line) = each ($fcontents)) {

  $parts = split (" ", $line);
  $fmonth = $parts[1];
  $fday = $parts[2];
  $fyear = $parts[0];
  $fhour = $parts[3];
  $fmin = $parts[4];
  $df_times[] = mktime($fhour,$fmin,0,$fmonth,$fday,$fyear);
  $df[] = $parts[11];
}

$times = Array();
$drct = Array();
$dwpf = Array();
$tmpf = Array();

$dbconn = iemdb('access');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE station = 'OT0006' 
  and dwpf > -99 and valid > '2010-01-01' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $drct[] = $row["drct"];
  $dwpf[] = $row["dwpf"];
  $tmpf[] = $row["tmpf"];
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,260,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(45,5,50,50);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h:i", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Dew Point [F]");

$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetTitleMargin(20);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Temperature [F]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->title->Set('Ames Instrumented House Timeseries');
$graph->xaxis->SetTitle('1 January 2010');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.09, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Outside Air Temp");
$lineplot->SetColor("red");
$graph->Add($lineplot);

$lineplot2=new LinePlot($df, $df_times);
$lineplot2->SetLegend("Deep Freeze Temp");
$lineplot2->SetColor("blue");
$graph->Add($lineplot2);


// Display the graph
$graph->Stroke();
?>
