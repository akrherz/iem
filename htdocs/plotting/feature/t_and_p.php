<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$phour = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, dwpf, p01m / 24.5 as phour
  from t2009 WHERE station = 'AMW' and valid > '2009-10-01' and dwpf > 0 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["dwpf"];
  $phour[] = $row["phour"];
  //$feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",20,90);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,5,5,100);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);


$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Des Moines Temperatures [F]");
$graph->y2axis->SetTitle("Des Moines Precip [inch]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.15,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Dew Point");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new BarPlot($phour,$times);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>
