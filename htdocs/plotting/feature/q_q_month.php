<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coop = iemdb("coop");

$xdata = Array();
$ydata = Array();
$data = Array();

$rs = pg_query($coop, "SELECT year, avg( (high+low)/2 ) as avg_temp 
      from alldata WHERE stationid = 'ia0000' and month = 7 
      GROUP by year ORDER by avg_temp ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $data[$row["year"]] = Array("july" => $i);
}
$rs = pg_query($coop, "SELECT year, avg( (high+low)/2 ) as avg_temp 
      from alldata WHERE stationid = 'ia0000' and month = 8 
      GROUP by year ORDER by avg_temp ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $data[$row["year"]]["august"] = $i;
}
reset($data);
while (list($year,$val) = each($data))
{
  $xdata[] = $val["july"] / 1.180 ;
  $ydata[] = $val["august"] / 1.180 ;
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,5,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);


$graph->yaxis->SetTitle("Predicted Pollen Competition [%]");
$graph->xaxis->SetTitle("Observed Outcrossing [%]");
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
$sc0=new ScatterPlot($xdata, $ydata);
$sc0->SetLegend("1.8m R^2=0.005");
$sc0->SetColor("blue");
$graph->Add($sc0);

// Display the graph
$graph->Stroke();
?>
