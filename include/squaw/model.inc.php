<?php
 /* The actual Flood Prediction Model! */


class flood_model
{

function flood_model($ts)
{
  $this->DEBUG = 2;
  $this->INFO = 1;
  $this->ERROR = 0;

	$this->basets = $ts;
    $this->message = "";
	$this->rainfall = Array();
	$this->baseflow = Array();
    $this->basinflow = Array();
	$this->totprec = Array();
	$this->cumprec = Array();
	$this->totrunoff = Array();
    for($i=0; $i < 13; $i++){
       $this->totprec[$i] = 0;
       $this->cumprec[$i] = 0;
       $this->totrunoff[$i] = 0;
       $this->basinflow[$i] = Array();
       for($j=0; $j < 240; $j++){
          $this->basinflow[$i][$j] = 0;
       }
    }
	$this->flow = Array();
	$this->obflow = Array();
    $this->storms = Array();
    $this->scenarios = Array();
    $this->selectedstorms = Array();
    $this->selectedscenarios = Array();
    $this->loglevel = $this->ERROR;
} // End of flood_model constructor

function logger($level, $s)
{
  if ($this->loglevel >= $level)    $this->message .= $s ." <br />\n";
}

function run()
{
	$this->loadScenarios();
	$this->loadRainfall();
	$this->computeRecessionCurve();
	$this->computeRunoff();
    $this->writeLogs();
} // End of run()

function computeRunoff()
{
	GLOBAL $basins;
    reset($this->rainfall);
    $debugT = "<table><tr><th>Basin</th><th>Rain</th><th>CN</th><th>5day</th>
         <th>TotRunoff</th><th>SRO</th><th>QPEAK</th><th>duradj</th>
         <th>toff(Storm)</th><th>toffset15</th></tr>";
	while (list($id, $event) = each($this->rainfall))
	{
		$basin = $event["basin"];
		$rain = $event["precip"];
        $debugT .= "<tr><td>$basin</td><td>$rain</td>";
		if ($rain == 0) continue;

		$this->cumprec[$basin] += $rain;

        /* Curve number is based on 5-Day total */
		$cn = $basins[$basin]["cn1"];
		if ($event['5day'] > 2.1) $cn = $basins[$basin]["cn3"];
		else if ($event['5day'] > 1.4) $cn = $basins[$basin]["cn2"];
        /* Add this rainfall into 5day value */
        //$this->rainfall[$id]['5day'] += $rain;

        $debugT .= "<td>$cn</td><td>". $event["5day"] ."</td>";
		$s = (1000.0 / $cn ) - 10.0;
		$sro = $this->totrunoff[$basin];

        /* Okay, base restraints 
        if (($cn > 90 && $rain > 0.25) || ($cn > 80 && $rain > 0.6) ||
            ($cn > 70 && $rain > 1.1)  || ($cn > 60 && $rain > 1.6) ) {

        } else {
             $debugT .= "<td colspan=\"6\">Minimum Precip & Curve Number not met</td></tr>";
             continue;
        }
        */

        /* Runoff does not include 5 day! */
		//$this->totrunoff[$basin] = pow($this->cumprec[$basin] - (0.2 * $s), 2)
		//					/ ($this->cumprec[$basin] + (0.8 * $s) );
        $this->totrunoff[$basin] = ($cn / 400.0) * $this->cumprec[$basin];
        //$this->totrunoff[$basin] = ($cn / 200.0) * $this->cumprec[$basin];
        $debugT .= "<td>". $this->totrunoff[$basin] ."</td>";
		$sro = ($this->totrunoff[$basin] - $sro);
		$qpeak = $basins[$basin]["qslope"] * $sro;
        $debugT .= "<td>$sro</td><td>$qpeak</td>";

		/* Adjust delivery of qpeak because of duration 1 h = 0 adjust */
		$duradj = ( 1.5 * (pow($event["dur"], 2) - 7 * $event["dur"] + 6)/-6)
				+ (3.75 * (pow($event["dur"], 2) - 4 * $event["dur"] + 3)/15);
        $debugT .= "<td>$duradj</td>";

		/* We need to compute an offset in our flow array to when this 
		   basin started to contribute. Units are hours for now */
		$toff = (($event["sts"] - $this->basets) / 3600.0);
        $debugT .= "<td>$toff</td>";

        $toff += $duradj;
		/* Now we offset this further by the delay it takes to get to the
		   gauge.  Units are still hours */
		$toff += ($basins[$basin]["delay"]);
		/* Now we convert to 15min intervals */
		$toffset15 = intval( $toff * 4 ) - $basins[$basin]['nrise'];
        $debugT .= "<td>$toffset15</td>";

      for ($tstep=0; $tstep < (240 - $toffset15); $tstep++)
      {
        $f = $qpeak /  2.0 * $basins[$basin]["curve"][$tstep] / 100.0;
        $this->basinflow[$basin][$tstep + $toffset15] += $f;
        $this->flow[$tstep + $toffset15] += $f;
      }
      $debugT .= "</tr>";
   }
   $debugT .= "</table>";
   $this->logger($this->INFO, $debugT);
} // End of computeRunoff

function writeLogs()
{
  GLOBAL $basins;
  $s = "TIME,OB,BASE,";
  for($j=0;$j<12;$j++)
  {
     $s .= $basins[$j]["name"] .",";
  }
  $s .= "MODEL\n";
  for($t=0;$t<240;$t++)
  {
    $s .= strftime('%Y-%m-%d %H:%M,' , $this->basets + ($t * 15*60)) ;
    $s .= sprintf('%.2f,', $this->obflow[$t]) ;
    $s .= sprintf('%.2f,', $this->baseflow[$t]) ;
    for($j=0;$j<12;$j++)
    {
      $s .= sprintf('%.2f,', $this->basinflow[$j][$t]);
    }
    $s .= sprintf('%.2f,', $this->flow[$t]);
    $s .= "\n";
  }

  $this->basinlogname = "../../tmp/". time() ."-log.dat";
  $fp = fopen($this->basinlogname, 'w');
  fwrite($fp, $s);
  fclose($fp);

}

function computeRecessionCurve()
{
	global $pg;

	/* First we initialize the flow array to zero */
	for ($tstep=0;$tstep<240;$tstep++)
	{
		$this->obflow[$tstep] = "";
	}
	/* Now we go fishing in the database! */
	$datestr = date("Y-m-d H:00", $this->basets);
	$sql = "SELECT * from real_flow WHERE valid >= '$datestr' and 
		valid < ('$datestr'::timestamp + '60 hours'::interval)";
	$rs = pg_query($pg, $sql);
	while($row = pg_fetch_array($rs))
	{
		$ts = strtotime( substr($row["valid"], 0, 16) );
		$tstep = ($ts - $this->basets) / 900.0;
		$this->obflow[$tstep] = $row["cfs"];
	}

	$t1 = ($this->r1ts - $this->basets) / 900.0;
	$t2 = ($this->r2ts - $this->basets) / 900.0;

	if (($this->obflow[$t1] > 0) && ($this->obflow[$t2] > 0) )
	{
		$this->logger($this->INFO, "<b>Real Flow Observations Found, using them instead.</b>");
        $this->logger($this->DEBUG, "T1: ". $this->obflow[$t1] ." T2: ". $this->obflow[$t2] );
		$this->rflow1 = $this->obflow[$t1];
		$this->rflow2 = $this->obflow[$t2];
	}

	if (($this->rflow2) > ($this->rflow1))
	{
		$this->logger($this->ERROR, "<b>WARNING:</b>  Failed receeding flow requirement. Assuming -1 cfs/hr rate.");
		$this->rflow1 = $this->rflow2 + (0.25 * ($t2 -$t1));
        $this->logger($this->DEBUG, "T1: ". $this->rflow1 ." T2: ". $this->rflow2 );
	
	}

	$this->logger($this->DEBUG, "computeRecessionCurve() t1 [$t1] t2 [$t2]");
	$bfr = pow( ($this->rflow1/$this->rflow2), (4.0/($t2-$t1)));
	$this->logger($this->DEBUG, "BFR $bfr ");
	for($tstep=0;$tstep<240; $tstep++)
	{
		$this->flow[$tstep] = ($this->rflow1)/( pow( ($bfr), (($t2 + $tstep)*0.25)) );
	}
	$this->baseflow = $this->flow;

} // End of computeRecessionCurve

function setSelectStorms($form)
{
  $this->selectedstorms = isset($form["storms"]) ? $form["storms"]: Array();

  global $pg;

  $datestr = date("Y-m-d H:00", $this->basets);
  /* We need to dig for cases if not set on website */
  $sql = "SELECT * from events WHERE onset >= '$datestr' and 
	 onset < ('$datestr'::timestamp + '60 hours'::interval) ORDER by onset ASC";
  $this->logger($this->DEBUG, $sql);
	$rs = pg_query($pg, $sql);
    $q = Array();
	while($row = pg_fetch_array($rs))
	{
		$this->storms[ $row["storm_id"] ] = 1;
        if ( $this->selectedstorms == "" || 
             in_array($row["storm_id"], $this->selectedstorms) )
        {
          $this->totprec[$row["basin_id"]] += $row["precip"];
		  $this->rainfall[] = Array("basin" => $row["basin_id"], 
			"precip" => $row["precip"], "dur" => $row["duration"],
            "5day" => 0,
			"sts" => strtotime(substr($row["onset"],0,16)) );
          $q[ $row["storm_id"] ] = 1;
        }
	}
    $a = Array();
    reset($q);
    while( list($k,$v) = each($q) )
    {
       $a[] = $k;
    }
    $this->selectedstorms = $a;
  $this->stormsSQL = "";
  if (sizeof($this->selectedstorms) > 0)
  {
    $this->stormsSQL = sprintf("and storm_id NOT IN (%s)", implode(",", $this->selectedstorms) );
    //$this->logger($this->DEBUG, $str);
  }
}

function setSelectScenarios($form)
{
  $this->selectedscenarios = isset($form["scenarios"]) ? $form["scenarios"]: Array();
}

/**
 * We load up scenarios that are in the DB
 */
function loadScenarios()
{
	global $pg;

    $sbase = mktime(0,0,0,1,1,2002); /* Base of our Scenarios */
	$sql = "SELECT * from scenario_events ORDER by onset ASC";
    $this->logger($this->DEBUG, $sql);
	$rs = pg_query($pg, $sql);
	while($row = pg_fetch_array($rs))
	{
		$this->scenarios[ $row["scenario_id"] ] = 1;
        if ( $this->selectedscenarios != "" && 
             in_array($row["scenario_id"], $this->selectedscenarios) )
        {
          $o = strtotime(substr($row["onset"],0,16));
          $this->totprec[$row["basin_id"]] += $row["precip"];
		  $this->rainfall[] = Array("basin" => $row["basin_id"], 
			"precip" => $row["precip"], "dur" => $row["duration"],
            "5day" => 0,
			"sts" => $this->basets + ($o - $sbase) );
        }
	}

	while (list($scenario_id,$v) = each($this->scenarios))
	{
		$sql = "SELECT * from scenarios WHERE id = $scenario_id ";
        $this->logger($this->DEBUG, $sql);
		$rs = pg_query($pg, $sql);
		$row = pg_fetch_array($rs);
        $this->scenarios[$scenario_id] = $row["name"];
        if ( $this->selectedscenarios != "" && 
             in_array($scenario_id, $this->selectedscenarios) )
        {
		  $this->logger($this->INFO, "Scenario ID: ". $row["name"] ." was used.");
        }
	}
}

function loadRainfall()
{
	global $pg;
	
    // We need to loop through and compute the 5day precip values 
    reset($this->rainfall);
	while (list($id, $event) = each($this->rainfall))
    {
       $odate = date("Y-m-d H:00", $event['sts'] );
       $sql = "SELECT sum(precip) as sum from events WHERE 
        basin_id = ". $event['basin'] ." and onset < '$odate'
        and onset > ('$odate'::timestamp - '5 days'::interval)";
       $this->logger($this->DEBUG, $sql);
       $rs = pg_query($pg, $sql);
       while( $row = pg_fetch_array($rs))
       {
          $this->rainfall[$id]['5day'] = $row["sum"];
       }
    }
    reset($this->storms);
	while (list($storm_id,$v) = each($this->storms))
	{
		$sql = "SELECT * from storms WHERE id = $storm_id ";
        $this->logger($this->DEBUG, $sql);
		$rs = pg_query($pg, $sql);
		$row = pg_fetch_array($rs);
        $this->storms[$storm_id] = $row["name"];
        if ( $this->selectedstorms == "" || 
             in_array($storm_id, $this->selectedstorms) )
        {
		  $this->logger($this->INFO, "Storm ID: ". $row["name"] ." was used.");
        }
	}
} // End of loadRainfall()

function addRecessionInfo($ts1, $flow1, $ts2, $flow2)
{
    if ( strlen($flow1) == 0 || strlen($flow2) == 0)
    {
       $this->logger($this->INFO, "No baseflow entered. Assuming 100 and 99");
       $flow1 = 100; $flow2 = 99;
    }
	$this->r1ts = $ts1;
	$this->r2ts = $ts2;
	$this->rflow1 = $flow1;
	$this->rflow2 = $flow2;

} // End of addRecessionInfo()

function printInfo()
{
	$s = "<h4>Peak Flows:</h4>
<table>
<thead>
<tr><th>Time Step:</th><th>Date/Time:</th><th>Flow (cfs):</th></tr>
</thead>
<tbody>";
	$m = 0;
	for ($tstep=1; $tstep<240; $tstep++)
	{
		if ($this->flow[$tstep - 1] < $this->flow[$tstep] 
			&& $this->flow[$tstep] > $this->flow[$tstep + 1])
		{
			$ts = $this->basets + ($tstep * 900);
			$st = strftime("%b %d @ %I:%M %p", $ts);
			$s .= "<tr><td> $tstep </td><td> $st </td><td> ". round($this->flow[$tstep],0) ."</td></tr>";
		}
	}
	$s .= "</table>";
	return $s;
}

function plot24HCurve()
{

	$xlabel = Array();
	$bankfull = Array();
	$flood = Array();
    $oldday = 0;
	for ($t=0; $t < 36*4; $t++)
	{
      $newday = strftime("%d", $this->basets + ($t * 900));
      if ($t == 0 || intval($newday) != intval($oldday) ) {   $fmt = "%d %b %I %p"; }
      else { $fmt = "%I %p"; }
      $xlabel[$t] = strftime($fmt, $this->basets + ($t * 900));
      $oldday = $newday;
	}
	for ($i=0.0; $i < 36*4; $i++)
	{
		$bankfull[$i] = 2650;
		$flood[$i] = 3700;
	}
    global $rootpath;
	include_once ("$rootpath/include/jpgraph/jpgraph.php");
	include_once ("$rootpath/include/jpgraph/jpgraph_line.php");
 
	$graph = new Graph(640,480,"example1");
	$graph->SetScale("textlin");
	$graph->setmargin(60,20,50,80);

	$graph->tabtitle->Set("Hydrograph");

	$graph->xaxis->SetTickLabels($xlabel);
	$graph->xaxis->SetTextTickInterval(4); 
	$graph->xaxis->SetLabelAngle(90);

	$graph->yaxis->SetTitle("Flow @ Gauge (cfs)");
	$graph->yaxis->SetTitleMargin(45);

    $graph->legend->Pos(0.01, 0.01);
    $graph->legend->SetLayout(LEGEND_HOR);

	$lineplot=new LinePlot( array_slice($this->flow, 0, 36*4) );
	$lineplot->SetColor("red");
	$lineplot->SetLegend("Predicted Flow");

	$lineplot2=new LinePlot( array_slice($this->baseflow, 0, 36*4) );
	$lineplot2->SetColor("blue");
	$lineplot2->SetLegend("Base Flow");
                                                                          
	$lineplot3=new LinePlot( array_slice($bankfull, 0, 36*4) );
	$lineplot3->SetColor("brown");
	$lineplot3->SetLegend("BankFull (2650)");
	$lineplot3->SetWeight(3);
                                                                          
	$lineplot4=new LinePlot( array_slice($flood, 0, 36*4) );
	$lineplot4->SetColor("green");
	$lineplot4->SetLegend("Flood (3700)");
	$lineplot4->SetWeight(3);
                                                                          
	$lineplot5=new LinePlot( array_slice($this->obflow, 0, 36*4) );
	$lineplot5->SetColor("black");
	$lineplot5->SetLegend("Ob Flow");
	$lineplot5->SetWeight(1);
                                                                          
	$graph->Add($lineplot5);
	$graph->Add($lineplot4);
	$graph->Add($lineplot3);
	$graph->Add($lineplot2);
	$graph->Add($lineplot);
	$fref = "../../tmp/24h_". time() .".png";
	$graph->Stroke($fref);
	return $fref;
} // End of plotRecessionCurve

function plotRecessionCurve()
{

	$xlabel = Array();
	$bankfull = Array();
	$flood = Array();
    $oldday = 0;
	for ($t=0; $t < 240; $t = $t + 12)
	{
      $newday = strftime("%d", $this->basets + ($t * 900));
      if ($t == 0 || intval($newday) != intval($oldday) ) {   $fmt = "%d %b %I %p"; }
      else { $fmt = "%I %p"; }
      $xlabel[$t] = strftime($fmt, $this->basets + ($t * 900));
      $oldday = $newday;
	}
	for ($i=0; $i < 240; $i++)
	{
		$bankfull[$i] = 2650;
		$flood[$i] = 3700;
	}
    global $rootpath;
	include_once ("$rootpath/include/jpgraph/jpgraph.php");
	include_once ("$rootpath/include/jpgraph/jpgraph_line.php");
 
	$graph = new Graph(640,480,"example1");
	$graph->SetScale("textlin");
	$graph->setmargin(60,20,50,80);

	$graph->tabtitle->Set("Hydrograph");

	$graph->xaxis->SetTickLabels($xlabel);
	$graph->xaxis->SetTextTickInterval(12); 
	$graph->xaxis->SetLabelAngle(90);

	$graph->yaxis->SetTitle("Flow @ Gauge (cfs)");
	$graph->yaxis->SetTitleMargin(45);

    $graph->legend->Pos(0.01, 0.01);
    $graph->legend->SetLayout(LEGEND_HOR);

	$lineplot=new LinePlot($this->flow);
	$lineplot->SetColor("red");
	$lineplot->SetLegend("Predicted Flow");

	$lineplot2=new LinePlot($this->baseflow);
	$lineplot2->SetColor("blue");
	$lineplot2->SetLegend("Base Flow");
                                                                          
	$lineplot3=new LinePlot($bankfull);
	$lineplot3->SetColor("brown");
	$lineplot3->SetLegend("BankFull (2650)");
	$lineplot3->SetWeight(3);
                                                                          
	$lineplot4=new LinePlot($flood);
	$lineplot4->SetColor("green");
	$lineplot4->SetLegend("Flood (3700)");
	$lineplot4->SetWeight(3);
                                                                          
	$lineplot5=new LinePlot( array_slice($this->obflow, 0, 240) );
	$lineplot5->SetColor("black");
	$lineplot5->SetLegend("Ob Flow");
	$lineplot5->SetWeight(1);
                                                                          
	$graph->Add($lineplot5);
	$graph->Add($lineplot4);
	$graph->Add($lineplot3);
	$graph->Add($lineplot2);
	$graph->Add($lineplot);
	$fref = "../../tmp/10d_". time() .".png";
	$graph->Stroke($fref);
	return $fref;
} // End of plotRecessionCurve

function rainfallMap()
{
	global $rootpath, $basins, $mapscript;
	dl($mapscript);

	$map = ms_newMapObj("$rootpath/data/gis/squaw.map");
	$map->set("width", 200);
	$map->set("height", 300);

    $map->setextent(420000.0, 4645000.0, 451000.0, 4686000.0);

	$img = $map->prepareImage();
	$background = $map->getLayerByName("background");
	$background->set("status", MS_ON);
	$background->draw($img);

	$counties = $map->getLayerByName("iacounties");
	$counties->set("status", MS_ON);
	$counties->draw($img);

	$basin = $map->getLayerByName("squaw_basin");
	$basin->set("status", MS_ON);
	$basin->draw($img);

	$b = $map->getLayerByName("basins");

	foreach($this->totprec as $id => $rain)
	{
		$pt = ms_newPointObj();
		$pt->setXY($basins[$id]["utm_x"], $basins[$id]["utm_y"]);
		$pt->draw($map, $b, $img, 0, $rain );
		$pt->free();

	}
    $map->drawLabelCache($img);


	$url = $img->saveWebImage();

	return $url;

}

} // End of Flood Model ?>
