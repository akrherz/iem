<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$station1 = "IFA";
$station2 = "CCY";

$times = Array($station1 => Array(), $station2 => Array() );
$data = Array($station1 => Array(), $station2 => Array() );

$dbconn = iemdb('access');
$sql = "SELECT station, valid, tmpf, dwpf, sknt, vsby
  from current_log WHERE station IN ('$station1','$station2') and valid > '2009-04-07' and valid < '2009-04-07 21:00' and dwpf > -99 and extract(minute from valid) NOT IN (15, 35, 55) ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $station = $row["station"];
  $dwpc = f2c($row["dwpf"]);
  $e = 6.11 * pow(10, 7.5 * $dwpc / (237.7 + $dwpc));
  $mixr = 0.62197 * $e / (1000.0 - $e);
  $times[$station][] = strtotime($row["valid"]);
  $data[$station][] = $mixr * 1000.0;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(50,5,50,85);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetTitle("Mixing Ratio [g/kg]");
$graph->yaxis->SetTitleMargin(35);
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('04/07/09 Snowmelt Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($data[$station1], $times[$station1]);
$lineplot->SetLegend("Iowa Falls [KIFA]");
$lineplot->SetColor("red");
$graph->Add($lineplot);

$lineplot3=new LinePlot($data[$station2],$times[$station2]);
$lineplot3->SetLegend("Charles City [KCCY]");
$lineplot3->SetColor("black");
$graph->Add($lineplot3);

// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
