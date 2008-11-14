<?php
// 1 minute schoolnet data plotter
// Cool.....
include("../../../config/settings.inc.php");

include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("IA_ASOS");
$cities = $nt->table;
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_led.php");

$station = isset($_GET["station"]) ? $_GET["station"] : "DSM";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");


  $myTime = strtotime($year."-".$month."-".$day);


$titleDate = strftime("%b %d, %Y", $myTime);
$tableName = strftime("t%Y_1minute", $myTime);
$sqlDate = strftime("%Y-%m-%d", $myTime);

/** Time to get data from database **/
$connection = iemdb("asos");
$query = "SELECT to_char(valid, 'HH24:MI') as tvalid, tmpf, dwpf from 
  ". $tableName ." WHERE station = '". $station ."' and 
  date(valid) = '". $sqlDate ."' ORDER by tvalid";

$result = pg_exec($connection, $query);

pg_close($connection);

if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

$tmpf = array();
$dwpf = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 100;
$max_yaxis = 0;

for( $p=0; $row = @pg_fetch_array($result,$p); $p++)  {
  $strDate = $sqlDate ." ". $row["tvalid"]; 
  $timestamp = strtotime($strDate );
#  echo $thisTime ."||";
  
  $thisTmpf = $row["tmpf"];
  $thisDwpf = $row["dwpf"];
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  } else {
    if ($max_yaxis < $thisTmpf){
      $max_yaxis = $thisTmpf;
    }
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = "";
  }  else {
    if ($min_yaxis > $thisDwpf){
      $min_yaxis = $thisDwpf;
    }
  }

  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $p ."-". $shouldbe ." - ". $timestamp ;
  
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    $tmpf[$i] = $thisTmpf;
    $dwpf[$i] = $thisDwpf;
    $xlabel[$i] = $row["tvalid"];
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $tmpf[$i] = "";
      $dwpf[$i] = "";
      $xlabel[$i] ="";
      $i++;
      $missing++;
    }
    $tmpf[$i] = $thisTmpf;
    $dwpf[$i] = $thisDwpf;
    $i++;
    continue;
    
    $q--;
  } else if (($timestamp - $shouldbe) < 0) {
#    echo "DUP <br>";
     $dups++;
    
  }

} // End of while

$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
        '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
        '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
        '8 PM', '9 PM', '10 PM', '11 PM', 'Midnight');


for ($j=0; $j<24; $j++){
  $xlabel[$j*60] = $xpre[$j];
}


// Fix y[0] problems
if ($tmpf[0] == ""){
  $tmpf[0] = 0;
}
if ($dwpf[0] == ""){
  $dwpf[0] = 0;
}




// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin", $min_yaxis - 4, $max_yaxis +4);
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yscale->SetGrace(10);
$graph->title->Set($cities[$station]['name'] ." Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07);



$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($dwpf);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

// Box for error notations
$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
$t1->SetPos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);

$graph->Add($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();

?>
