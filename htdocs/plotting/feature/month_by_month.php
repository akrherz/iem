<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coop = iemdb('coop');

$ar1 = Array();
$rs = pg_query($coop, "select east.month, count(*) as total, 
  sum(case when east.high > west.high THEN 1 ELSE 0 END) as hits 
  from (select day, month, high from alldata where stationid = 'ia7708' 
        and year between 1950 and 2009) as west, 
       (select day, month, high from alldata where stationid = 'ia2364' 
        and year between 1950 and 2009) as east 
  WHERE east.day = west.day GROUP by east.month ORDER by east.month ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $ar1[] = $row["hits"] / floatval($row["total"]) * 100.0;
}

$ar2 = Array();
$rs = pg_query($coop, "select north.month, count(*) as total, 
  sum(case when north.high > south.high THEN 1 ELSE 0 END) as hits 
  from (select day, month, high from alldata where stationid = 'ia4585' 
        and year between 1950 and 2009) as south, 
       (select day, month, high from alldata where stationid = 'ia5230' 
        and year between 1950 and 2009) as north 
  WHERE north.day = south.day GROUP by north.month ORDER by north.month ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $ar2[] = $row["hits"] / floatval($row["total"]) * 100.0;
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("textlin");

$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,0,25,60);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels( Array("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP","OCT", "NOV", "DEC") );
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,14);
$graph->yaxis->SetTitle("Percentage Occurance");
$graph->title->Set('1951-2008 Warmer High Temperature');
$graph->title->SetFont(FF_ARIAL,FS_BOLD,10);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.95, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot( $ar1 );
$lineplot->SetLegend("Dubuque > Sioux City");
$lineplot->SetFillColor("blue");
$lineplot->value->Show();
$lineplot->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot->value->SetFormat('%.0f');
//$lineplot->SetWidth(1);

// Create the linear plot
$lineplot2=new BarPlot( $ar2 );
$lineplot2->SetLegend("Mason City > Lamoni");
$lineplot2->SetFillColor("red");
$lineplot2->value->Show();
$lineplot2->value->SetFont(FF_ARIAL,FS_BOLD,10);
$lineplot2->value->SetFormat('%.0f');
//$lineplot2->value->SetColor('black');
//$lineplot2->SetWidth(1);

$gbarplot = new GroupBarPlot(array($lineplot,$lineplot2));
$gbarplot->SetWidth(0.6);
$graph->Add($gbarplot);

// Display the graph
$graph->Stroke();
?>
