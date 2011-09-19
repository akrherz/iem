<?php
include("../../../config/settings.inc.php");
//  1 minute data plotter 

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$station = isset($_REQUEST['station']) ? $_REQUEST['station']: null;

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$tmpf = array();
$relh = array();
$valid = array();

if ($station == null){
	$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
	while (list ($line_num, $line) = each ($fcontents)) {
		$parts = preg_split ("/\s+/", $line);
  		$valid[] = strtotime( substr($line, 0, 26) );
  		$tmpf[] = round (substr($line, 36, 6),2);
  		$relh[] = intval($parts[7]);
 	} // End of while
} else {
	$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0010.dat");
	/*
	 * month, day, year, hour, minute, outside temp, hi outside temp, lo outside
       temp, outside humidity, wind speed, wind direction, wind gust speed, time
 		of gust, pressure, daily_precip, monthly_rain, yearly_rain, inside
 		temp, inside humidity, solar radiation, UV index
	 */
	while (list ($line_num, $line) = each ($fcontents)) {
		$tokens = explode(' ', $line);
		if (sizeof($tokens) != 21){
			continue;
		}
  		$tstring = sprintf("%s %s", $dirRef, $tokens[3]);
  		$valid[] = strtotime($tstring);
  		$tmpf[] = $tokens[5];
  		$relh[] = floatval($tokens[8]);
 	} // End of while
	
}
	
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin",0,100);

$graph->img->SetMargin(65,40,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yaxis->scale->ticks->Set(1,0.5);
//$graph->yscale->SetGrace(10);
$graph->title->Set("Outside Temperature & Relative Humidity");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.065);


$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->y2axis->SetTitle("Relative Humidity [%]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $valid);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
//[DMF]$lineplot2=new LinePlot($dwpf);
//[DMF]$lineplot2->SetLegend("Dew Point");
//[DMF]$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($relh, $valid);
$lineplot3->SetLegend("Rel Humid");
$lineplot3->SetColor("black");

// Box for error notations
//[DMF]$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//[DMF]$t1->SetPos(0.4,0.95);
//[DMF]$t1->SetOrientation("h");
//[DMF]$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//[DMF]$t1->SetColor("black");
//[DMF]$graph->AddText($t1);

//[DMF]$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke();

?>
