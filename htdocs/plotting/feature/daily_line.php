<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");



$dbconn = iemdb('coop');
$times = Array();
$data = Array();

$sql = "select sday, count(*), avg(count) from (select day, sday, count(*) from alldata WHERE precip > 0.99 and sday != '0229' GROUP by day, sday) as foo GROUP by sday ORDER by sday ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = mktime(6,0,0, substr($row["sday"],0,2), substr($row["sday"],2,2),2009);
  $data[] = $row["avg"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(60,5,45,70);
$graph->SetMarginColor('white');
$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->ygrid->SetLineStyle('dashed');
$graph->ygrid->SetColor('gray');
$graph->xgrid->Show();
$graph->xgrid->SetLineStyle('dashed');
$graph->xgrid->SetColor('gray');

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(70);

$graph->title->Set("Frequency of Daily Above Freezing High + Below Freezing Low");

$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Observed Frequency [%]");
$graph->xaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->SetFont(FF_FONT2,FS_BOLD,16);
$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->subtitle->Set('Ames [1893-2008]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.6,0.15, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->Show();
  $graph->xgrid->Show();

function tb($a){
  return date('M d', $a);
  //return '';
}

$graph->xaxis->SetLabelFormatCallback('tb');
$graph->xaxis-> scale->ticks->Set(86400,86400*14);

reset($times);
while (list($k,$v) = each($times))
{
 if (date("d", $v) == 1) {
  // $graph->AddLine(new PlotLine(VERTICAL,$v,"gray",1));
 }
}
 
// Create the linear plot
$lineplot=new LinePlot($data, $times);
//$lineplot->SetLegend("Highs");
$lineplot->SetFillColor('skyblue@0.2');
$lineplot->SetColor('navy@0.7');
$graph->Add($lineplot);



// Display the graph
$graph->Stroke();
?>
