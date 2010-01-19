<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$dbconn = iemdb('asos');
include("$rootpath/include/mlib.php");

$years = Array();
$dwpf = Array();

for ($year=1973;$year<2010;$year++) {

  $sql = "SELECT round(avg(dwpf)::numeric,1) as dew
    from t${year} WHERE station = 'DSM' and dwpf > -50 and
    valid BETWEEN '${year}-07-01' and '${year}-08-01'";
  $rs = pg_query($dbconn, $sql);
  $row=@pg_fetch_array($rs,0);
  $years[] = $year;
  $dwpf[] = $row["dew"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,480,"example1");
$graph->SetScale("textlin",56,70);
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,5,30,50);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($years);

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Visibility [mile]");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Dew Point Temperature [F]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Des Moines [KDSM] Avg Jul Dew Point');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();
$graph->xaxis->SetTextLabelInterval( 2 );

// Create the linear plot
$bplot=new BarPlot($dwpf);
//$bplot->SetLegend("2009");
$bplot->SetColor("blue");
$graph->Add($bplot);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));

// Display the graph
$graph->Stroke();
?>
