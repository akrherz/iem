<?php
// 1 minute schoolnet data plotter
// Cool.....
// 16 Sep 2002:	Account for bad RH data
//  4 Dec 2002:	Account for those negative temps
// 18 Dec 2003	We need to do some tricks to account for sites with very
//		little reporting (temporally)
//  3 Apr 2005  What the heck am I doing?

include ("../../include/snetLoc.php");

$station = isset( $_GET["station"] ) ? intval($SconvBack[ $_GET["station"] ]): 'SKCI4';
$year = isset( $_GET["year"] ) ? $_GET["year"] : date("%Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("%m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("%d");

$myTime = strtotime($year."-".$month."-".$day);
$dirRef = strftime("%Y_%m/%d", $myTime);
$matchDate = strftime("%m/%d/%y", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);
$fcontents1 = file('/mesonet/ARCHIVE/raw/snet/2005_04/03/'.$station.'.dat');
$fcontents2 = file('/mesonet/ARCHIVE/raw/snet/2005_04/02/'.$station.'.dat');

$sr1 = array();
$sr2 = array();
$xlabel = array();
for ($i=0;$i<=1440;$i++)
{
  $sr1[$i] = " ";
  $sr2[$i] = " ";
}

$start = intval( $myTime );
$i = 0;

$min_yaxis = 100;
$max_yaxis = 0;

while (list ($line_num, $line) = each ($fcontents1)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];

  $hhmm = split (":", $thisTime);
  $offset = intval($hhmm[0]) * 60 + intval($hhmm[1]);

  $thisSR = intval( substr($parts[4],0,3) ) * 10;
  $sr1[$offset] = $thisSR;
} // End of while
while (list ($line_num, $line) = each ($fcontents2)) {
  $parts = split (",", $line);
  $thisTime = $parts[0];

  $hhmm = split (":", $thisTime);
  $offset = intval($hhmm[0]) * 60 + intval($hhmm[1]);

  $thisSR = intval( substr($parts[4],0,3) ) * 10;
  $sr2[$offset] = $thisSR;
} // End of while


$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
        '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
        '8 PM', '9 PM', '10 PM', '11 PM', 'Midnight');


for ($j=0; $j<25; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


// Fix y[0] problems
if ($tmpf[0] == ""){
  $tmpf[0] = 0;
}
if ($dwpf[0] == ""){
  $dwpf[0] = 0;
}
if ($sr[0] == ""){
  $sr1[0] = 0;
  $sr2[0] = 0;
}


include ("../dev17/jpgraph.php");
include ("../dev17/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(250,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(55,5,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(120);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yscale->SetGrace(10);
$graph->title->Set($Scities[$Sconv[$station]]['city'] ." SNET");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

$graph->yaxis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);

$graph->yaxis->SetTitle("Solar Radiation [Wm**-2]");
$graph->yaxis->SetTitleMargin(35);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->yaxis->SetTitleMargin(48);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot2=new LinePlot($sr1);
$lineplot2->SetLegend("Solar Rad 3 Apr");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($sr2);
$lineplot3->SetLegend("Solar Rad 2 Apr");
$lineplot3->SetColor("red");

// Box for error notations
//$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//$t1->Pos(0.4,0.95);
//$t1->SetOrientation("h");
//$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//$t1->SetColor("black");
//$graph->AddText($t1);

$graph->Add($lineplot3);
$graph->Add($lineplot2);

$graph->Stroke();

?>
