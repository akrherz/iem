<?php
include_once("$rootpath/include/database.inc.php");


class selectWidget
{
  var $appurl = '';
  var $destination = '';
  var $imgurl = '';
  var $showCamera = true;
  var $showRADAR = true;
  var $map = '';
  var $imgsz_y = 360;
  var $imgsz_x = 480;
  var $selectedSite = '';
  var $extents = '';
  var $fullextents = '';
  var $network = 'IA_ASOS';
  var $netlib = Array(
   "IACLIMATE" => "Iowa Climate Sites",
   "IA_COOP" => "Iowa NWS COOP Sites",
   "IACOCORAHS" => "Iowa CoCoRaHS",
   "COOPDB" =>"Iowa Climate Sites",
   "ISUAG" =>"ISU Ag Climate",
   "IA_ASOS" => "Iowa ASOS",
   "AWOS" => "Iowa AWOS",
   "IA_RWIS" => "Iowa RWIS",
   "DCP" => "Iowa DCP Sites",
   "IA_RAWS" => "Iowa RAWS Sites",
   "KCCI" => "KCCI-TV SchoolNet8",
   "KELO" => "KELO-TV WeatherNet",
   "KIMT" => "KIMT-TV StormNet",
   "IL_ASOS" => "Illinois ASOS",
   "IN_ASOS" => "Indiana ASOS",
   "KS_ASOS" => "Kansas ASOS",
   "MI_ASOS" => "Michigan ASOS",
   "MN_ASOS" => "Minnesota ASOS",
   "MO_ASOS" => "Missouri ASOS",
   "ND_ASOS" => "North Dakota ASOS",
   "NE_ASOS" => "Nebraska ASOS",
   "OH_ASOS" => "Ohio ASOS",
   "SD_ASOS" => "South Dakota ASOS",
   "WI_ASOS" => "Wisconsin ASOS",
   "KS_RWIS" => "Kansas RWIS",
   "MN_RWIS" => "Minnesota RWIS",
   "WI_RWIS" => "Wisconsin RWIS",
  );
  // 4x3
  var $presets = Array(
   "KCCI" => Array(220000, 4490000, 620000, 4790000),
   "KIMT" => Array(420000, 4640000, 620000, 4890000),
   "KELO" => Array(-400833, 4626666,399166,5226666),
   "COOPDB" => Array(175000, 4400000, 775000, 4850000),
   "IACLIMATE" => Array(175000, 4400000, 775000, 4850000),
   "IACOCORAHS" => Array(175000, 4400000, 775000, 4850000),
   "ISUAG" => Array(175000, 4400000, 775000, 4850000),
   "ISUAG" => Array(175000, 4400000, 775000, 4850000),
   "IA_RWIS" => Array(175000, 4400000, 775000, 4850000),
   "KS_RWIS" => Array(-332765, 4092099, 391358, 4419242),
   "WI_RWIS" => Array(575000, 4700000, 1175000, 5150000),
   "MN_RWIS" => Array(110000, 4700000, 775000, 5500000),
   "IA_COOP" => Array(175000, 4400000, 775000, 4850000),
   "DCP" => Array(175000, 4400000, 775000, 4850000),
   "IA_RAWS" => Array(175000, 4400000, 775000, 4850000),
   "SCAN" => Array(175000, 4400000, 775000, 4850000),
   "OT" => Array(175000, 4400000, 775000, 4850000),
   "AWOS" => Array(175000, 4400000, 775000, 4850000),
   "IA_ASOS" => Array(175000, 4400000, 775000, 4850000),
   "IL_ASOS" => Array(620917, 4063582, 990083, 4750925),
   "IN_ASOS" => Array(940979, 4185564, 1189029, 4688185),
   "KS_ASOS" => Array(-332765, 4092099, 391358, 4419242),
   "MI_ASOS" => Array(699532, 4583808, 1329337, 5270880),
   "MN_ASOS" => Array(110000, 4700000, 775000, 5500000),
   "MO_ASOS" => Array(288643, 4031077, 830891, 4501118),
   "NE_ASOS" => Array(-443050, 4449533, 309260, 4789607),
   "ND_ASOS" => Array(-372922, 5109273,268869, 5409961),
   "OH_ASOS" => Array(1193810, 4322261, 1565503, 4739477),
   "SD_ASOS" => Array(-400833, 4626666,399166,5226666),
   "WI_ASOS" => Array(575000, 4700000, 1175000, 5150000),
  );
  var $formvars = Array();
  var $networks = Array();

  function selectWidget($myapp, $mydestination, $mynetwork)
  {
    global $mapscript, $rootpath;
    dl($mapscript);
    $this->map = ms_newMapObj("$rootpath/data/gis/base26915.map");
    $this->destination = $mydestination;
    $this->networks[] = $mynetwork;
	$this->appurl = $myapp;
	$this->network = $mynetwork;
	$this->extents = $this->presets[$mynetwork];
	$this->fullextents = $this->presets[$mynetwork];
  }

  function set_networks($myvar)
  {
    if ($myvar == "ALL"){  
      while (list($k,$v) = each($this->netlib))
      {
        $this->networks[] = $k;
      }
      return;
    }
    $this->networks = $myvar;
  }

  function setformvars($myar)
  {
	$this->formvars = $myar;
  }
  function logic($f)
  {
	/** If zoom is 100, we go to full-view */
	if (array_key_exists('zoom', $f) && $f["zoom"] == 100)
	{
		$this->extents = $this->fullextents;
	}
	/** If zoom is set, then we need to do a map operation */
	if (array_key_exists('zoom', $f) && isset($f["map_x"]) )
	{
		/** If zoom is 0, we are querying! */
		if ($f["zoom"] == 0)
		{
			$this->performQuery($f);
			if ($this->selectedSite != '')
			{
				//echo "+++ Selected Site is: ". $this->selectedSite ." +++<br>";
				$this->forward();
			}
		}
		else 
		{
			$this->click2geo($f["extents"], $f["map_x"], $f["map_y"], $f["zoom"]);
			$this->drawMap();
		}
	}
	else {
		$this->drawMap();
	}
  }
  function forward()
  {
	$fin = $this->destination;
	while (list($key,$val) = each($this->formvars))
	{
		$fin .= "&$key=$val";
	}
	header("Location: ". $fin ."&station=". $this->selectedSite );
	exit();
  }
  function click2geo($oextents, $click_x, $click_y, $zoom)
	{
	//echo "+++ click2geo +++<br>";
	$arExtents = explode(",", $oextents);
	$ll_x = $arExtents[0];
	$ll_y = $arExtents[1];
	$ur_x = $arExtents[2];
	$ur_y = $arExtents[3];
//  print_r($arExtents);

	$dy = ($ur_y - $ll_y) / floatval($this->imgsz_y);
	$dx = ($ur_x - $ll_x) / floatval($this->imgsz_x);

	$centerX = ($click_x * $dx) + $ll_x ; 
	$centerY = $ur_y - ($click_y * $dy) ;

	if (intval($zoom) < 0)
    $zoom = -1 / intval($zoom) ; 

	$n_ll_x = $centerX - (($dx * $zoom) * ($this->imgsz_x / 2.00));
	$n_ur_x = $centerX + (($dx * $zoom) * ($this->imgsz_x / 2.00));
	$n_ll_y = $centerY - (($dy * $zoom) * ($this->imgsz_y / 2.00));
	$n_ur_y = $centerY + (($dy * $zoom) * ($this->imgsz_y / 2.00));

	$this->extents = Array($n_ll_x, $n_ll_y, $n_ur_x, $n_ur_y);
  }
  function performQuery($form)
  {
    global $_DATABASES;
	//echo "+++ performQuery +++<br>";
    //if (! isset($form["map_x"]) ) return;
    /** Get the click event from the form */
    $click_x = $form["map_x"];
    $click_y = $form["map_y"];

	$arExtents = explode(",", $form["extents"]);
	$ll_x = $arExtents[0];
	$ll_y = $arExtents[1];
	$ur_x = $arExtents[2];
	$ur_y = $arExtents[3];    

    $dy = ($ur_y - $ll_y) / floatval($this->imgsz_y);
    $dx = ($ur_x - $ll_x) / floatval($this->imgsz_x);
 
    $centerX = ($click_x * $dx) + $ll_x ;
    $centerY = $ur_y - ($click_y * $dy) ;
 
    $click = ms_newPointObj();
    $click->setXY($centerX, $centerY);

	//$p4326 = ms_newprojectionobj("init=epsg:4326");
	//$p26915 = ms_newprojectionobj("init=epsg:26915");
	//$click->project($p26915, $p4326);
	//print_r($click);
    $sites = $this->map->getlayerbyname("sites");
    $sites->set("connection", $_DATABASES["mesosite"]);
    $sites->set("status", MS_ON);
	$sites->setfilter("network = '". $this->network ."'");
    $sites->queryByPoint($click, MS_SINGLE, -1);
    $sites->open();
    $rs = $sites->getresult(0);
    $shp = $sites->getShape(-1,  $rs->shapeindex);
	//print_r($shp);
	//print_r($rs);
    $this->selectedSite = $shp->values["id"];
    //echo $this->selectedSite;
    //echo $this->network;
  }
  function drawMap()
  {
    global $_DATABASES;
	$this->map->setextent($this->extents[0], $this->extents[1], 
							$this->extents[2], $this->extents[3]);
    $sites = $this->map->getlayerbyname("sites");
    $sites->set("connection", $_DATABASES["mesosite"]);
    $sites->set("status", MS_ON);
    $sites->setfilter("network = '". $this->network ."'");
    if (! $this->showCamera)
    {
      $sites_c0 = $sites->getClass(0);
      $sites_c0->setexpression("ZZZZZ");
    }

    $counties = $this->map->getlayerbyname("counties");
    $counties->set("status", MS_ON);

    $states = $this->map->getlayerbyname("states");
    $states->set("status", MS_ON);
    

    $img = $this->map->prepareImage();
    $counties->draw($img);
    $states->draw($img);
    $sites->draw($img);
    $this->map->drawLabelCache($img);
    $this->imgurl = $img->saveWebImage();

    $this->extents = Array( $this->map->extent->minx, 
        $this->map->extent->miny, $this->map->extent->maxx,
        $this->map->extent->maxy);
  }
  function setShowRADAR($choice)
  {
    $this->showRADAR = $choice;
  }

  function printInterface()
  {
    global $rooturl;
	$s = "<form method=\"GET\" name=\"selectwidget\" action=\"". $this->appurl ."\">\n";
	while (list($key,$val) = each($this->formvars))
	{
		$s .= "<input type=\"hidden\" name=\"$key\"  value=\"$val\">\n";
	}
	$s .= "<input type=\"hidden\" name=\"zoom\" value=\"0\">\n";
	$s .= "<input type=\"hidden\" name=\"network\" value=\"". $this->network ."\">\n";
    $s .= "<input type=\"hidden\" name=\"extents\" value=\"". $this->extents[0] .", ". $this->extents[1] .", ".$this->extents[2] .", ".$this->extents[3] ."\">\n";
    $s .= "<script Language=\"JavaScript\">
 function resetButtons(){
   document.panButton.src = '$rooturl/images/button_pan_off.png';
   document.zoominButton.src = '$rooturl/images/button_zoomin_off.png';
   document.zoomoutButton.src = '$rooturl/images/button_zoomout_off.png';
   document.queryButton.src = '$rooturl/images/button_query_off.png';
   document.zoomfullButton.src = '$rooturl/images/button_zoomfull_off.png';
 }
</script>
<div style=\"margin: 2px; border: 0px; padding: 0px; text-align: left; width: 520px; height: 400px;\">
<span style=\"height: 25px; padding: 3px; letter-spacing: 0.3em; font-weight: bold; background: #cc0; float: left;\">IEM Site Selector:</span>
    <div style=\"float: right; font-weight: bold;\">Select Network:". $this->networkSelectInterface() ."</div><br clear=\"all\"/>
<div style=\"float: left; background: #cc0; padding-top: 10px; padding-left: 2px; padding-right: 2px; \">
<img src=\"$rooturl/images/button_zoomin_off.png\" name=\"zoominButton\" alt=\"Zoom In\" onClick=\"javascript: resetButtons(); document.zoominButton.src = '$rooturl/images/button_zoomin_on.png'; document.selectwidget.zoom.value = -2;\"><br />
<img src=\"$rooturl/images/button_pan_off.png\" name=\"panButton\" alt=\"Pan\" onClick=\"javascript: resetButtons(); document.panButton.src = '$rooturl/images/button_pan_on.png'; document.selectwidget.zoom.value = 1;\"><br />
<img src=\"$rooturl/images/button_zoomout_off.png\" name=\"zoomoutButton\" alt=\"Zoom Out\" onClick=\"javascript: resetButtons(); document.zoomoutButton.src = '$rooturl/images/button_zoomout_on.png'; document.selectwidget.zoom.value = 2;\"><br />
<img src=\"$rooturl/images/button_query_on.png\" name=\"queryButton\" alt=\"Select\" onClick=\"javascript: resetButtons(); document.queryButton.src = '$rooturl/images/button_query_on.png'; document.selectwidget.zoom.value = 0;\"><br />
<img src=\"$rooturl/images/button_zoomfull_off.png\" name=\"zoomfullButton\" alt=\"Zoom Full\" onClick=\"javascript: resetButtons(); document.zoomfullButton.src = '$rooturl/images/button_zoomfull_on.png'; document.selectwidget.zoom.value = 100; document.selectwidget.submit(); \"><br />
</div>";
	$s .= "<div style=\"background: #cc0; float: left; padding: 3px;\"><input type=\"image\" name=\"map\" src=\"". $this->imgurl ."\" border=0></div>";
    $s .= "</div></form>";
    return $s;
 }
 
 function networkSelectInterface()
 {
   $s = "<SELECT name=\"network\" onChange=\"javascript: this.form.submit() \">";
reset($this->networks);
while( list($k, $v) = each($this->networks) )
{
   $s .= "<option value=\"$v\"";
   if ($this->network == $v) $s .= " SELECTED ";
   $s .= ">". $this->netlib[$v] ." \n";
}
    $s .= "</select>\n";
    return $s;
  } 

  function siteSelectInterface($selected)
  {
     global $rootpath;
     include_once("$rootpath/include/database.inc.php");
     $s = "<select name=\"station\" onChange=\"javascript: this.form.submit()\">";
     /* Query database for stations! */
     $conn = iemdb("mesosite");
     $rs = pg_exec($conn, "SELECT *  from stations WHERE 
                           network = '". $this->network ."' ORDER by name ASC");
     pg_close($conn);
     for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
     {
        $s .= "<option value=\"". $row["id"] ."\"";
        if ($row["id"] == $selected) $s .= " SELECTED "; 
        $s .= ">". $row["name"] ."</option>\n";
     }
     $s .= "</select>";
     return $s;
  }

} // End of selectWidget
