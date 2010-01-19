<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$data = Array();

$asos = iemdb('asos');

for($year=1973;$year<2009;$year++)
{
  $sql = "SELECT tmpf, drct, sknt
  from t$year WHERE station = 'DSM' and valid BETWEEN '${year}-08-01' 
  and '${year}-08-31'
  and sknt >= 0 and drct >= 0 and tmpf > -40 and extract(hour from valid) = 14";
  $rs = pg_query($asos, $sql);

  for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
  {
    if (! array_key_exists($row["drct"], $data) ){ $data[$row["drct"]] = Array(); }
    $data[$row["drct"]][] = $row["tmpf"];
  }
}

$bins = Array();
for($i=0;$i<360;$i=$i+10){
  $bins[] = array_sum($data[$i]) / sizeof($data[$i]);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(620,480);
$graph->SetScale("textlin",70,90);
$graph->img->SetMargin(45,13,25,45);

//$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);
$graph->xaxis->HideTicks();
$graph->xaxis->SetTickLabels( Array("North","","","","","","","","",
                                    "East","","","","","","","","",
                                    "South","","","","","","","","",
                                    "West","","","","","","","","North") );


$graph->yaxis->SetTitle("Mean Air Temperature [F]");
$graph->xaxis->SetTitle("Wind Direction");
$graph->tabtitle->Set('2 PM August Des Moines [1973-2008]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.01,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc1=new BarPlot($bins);
$graph->Add($sc1);

// Display the graph
$graph->Stroke();
?>
