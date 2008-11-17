<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/all_locs.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$dwpf = Array();
$feel = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt
  from t2008 WHERE station = 'DSM' and valid > '2008-11-01' and dwpf > -99 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["tmpf"];
  $dwpf[] = $row["dwpf"];
  $feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,5,5,100);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);


$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Des Moines Temperature [F]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($dwpf, $times);
$lineplot->SetLegend("Dew Point");
$lineplot->SetColor("blue");

// Create the linear plot
$lineplot2=new LinePlot($tmpf,$times);
$lineplot2->SetLegend("Temp");
$lineplot2->SetColor("red");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>
