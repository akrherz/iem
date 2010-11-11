<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$data = Array();
$years = Array();
$dbconn = iemdb('asos');
for($year=1970;$year<2011;$year++){
  $sql = "SELECT tmpf, dwpf
  from t${year} WHERE station = 'DSM' and valid > '${year}-07-01' 
  and valid < '${year}-08-17' and dwpf > -99 and tmpf > -99";
  $rs = pg_query($dbconn, $sql);
  $total = 0;
  for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
  {
   $dwpc = f2c($row["dwpf"]);
   $e = 6.11 * pow(10, 7.5 * $dwpc / (237.7 + $dwpc));
   $mixr = 0.62197 * $e / (1000.0 - $e);
   $total += $mixr * 1000.0;
  }

  $data[] = $total / floatval(pg_num_rows($rs)); 
  $years[] = $year;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(310,290,"example1");
$graph->SetScale("textlin",11,16);
$graph->img->SetMargin(50,5,50,45);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->HideTicks();
//$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetTextTickInterval(5);

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetTitle("Avg Mixing Ratio [g/kg]");
$graph->yaxis->SetTitleMargin(35);
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Des Moines [KDSM], 1 Jul - 17 Aug ');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();



$lineplot3=new BarPlot($data);
//$lineplot3->SetLegend("Charles City KCCY");
//$lineplot3->SetColor("black");
$graph->Add($lineplot3);

// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
