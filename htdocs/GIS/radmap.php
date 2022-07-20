<?php
/* 
 * I am sort of inspired by the old mapblaster days.  Lets create a map of
 * all sorts of data with tons of CGI vars, yippeee
 * 
 */

require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";
require_once "../../include/forms.php";
$postgis = iemdb("postgis");

$plotmeta = Array("title" => Array(),
	"subtitle" => "");

function draw_header($map, $img, $width, $height){
	/*
	 * Draw the black bar at the top of the screen
	 */
	$layer = ms_newLayerObj($map);
	$layer->set("status", MS_ON );
	$layer->set("type", MS_LAYER_POLYGON );
	$layer->set("transform", MS_OFF );
	$wkt = "POLYGON((0 0, 0 $height, $width $height, $width 0, 0 0))";
	$layer->addFeature(ms_shapeObjFromWkt($wkt));

	$layerc0 = ms_newClassObj($layer);
	$layerc0s0 = ms_newStyleObj($layerc0);
	$layerc0s0->color->setRGB(0,0,0);
	$layer->draw($img);
}

function get_goes_fn_and_time($ts, $sector, $product){
	/*
	 * Return a filename or NULL for a requested GOES Product and time
	 * using a crude search algorithm
	 */
	$base = "/mesonet/ARCHIVE/data/";
	for($i=0;$i<60;$i++){
		foreach (array(1,-1) as $mul){
			$lts = $ts + ($i*60*$mul);
			$testfn = $base . gmdate("Y/m/d", $lts) ."/GIS/sat/awips211/GOES_${sector}_${product}_".
					gmdate("YmdHi", $lts) .".png";
			if (is_file($testfn)){
				return Array($testfn, $lts);
			}
		}
	}
	return Array(NULL,NULL);
}

function get_ridge_fn_and_time($ts, $radar, $product){
	/*
	 * Return a filename or NULL for a requested RIDGE Product and time
	 * using a crude search algorithm
	 */
	$base = "/mesonet/ARCHIVE/data/";
	for($i=0;$i<10;$i++){
		foreach (array(1,-1) as $mul){
			$lts = $ts + ($i*60*$mul);
			$testfn = $base . gmdate("Y/m/d", $lts) ."/GIS/ridge/$radar/$product/${radar}_${product}_".
					gmdate("YmdHi", $lts) .".png";
			if (is_file($testfn)){
				return Array($testfn, $lts);
			}
		}
	}
	return Array(NULL,NULL);
}

$sectors = Array(
 "iem" => Array("epsg" => 4326, "ext" => Array(-100.0, 38.5, -88.0, 46.5)),
 "lot" => Array("epsg" => 4326, "ext" => Array(-94.8, 39.0, -83.5, 46.5)),
 "ict" => Array("epsg" => 4326, "ext" => Array(-102.4, 35.45, -94.4, 40.35)),
 "sd" => Array("epsg" => 4326, "ext" => Array(-105.5, 40.5, -95.5, 48.0)),
 "hun" => Array("epsg" => 4326, "ext" => Array(-90.0, 32.0, -84.0, 36.0)),
 "conus" => Array("epsg" => 2163, 
         "ext" => Array(-2110437, -2251067, 2548326, 1239063)),
 "texas" => Array("epsg" => 2163, 
         "ext" => Array(-532031.375, -2133488,723680.125, -959689.625)),
 "etexas" => Array("epsg" => 2163, 
         "ext" => Array(-132031.375, -1933488,623680.125, -1259689.625)),
 "florida" => Array("epsg" => 2163, 
         "ext" => Array(1184257, -2271667,2198502, -1189456)),
 "maine" => Array("epsg" => 2163, 
         "ext" => Array(2201008.54544837, 209411.348773363,2516387.56069489, 732383.197334035)),
 "michigan" => Array("epsg" => 26915, 
         "ext" => Array(697867.530690471, 4641622.22153389,1363156.86711036, 5347664.58607328)),
 "washington" => Array("epsg" => 2163, 
         "ext" => Array(-1816611.94664531, 247411.313142634,-1231350.67314885, 688254.98213837)),
 "california" => Array("epsg" => 2163, 
         "ext" => Array(-2031905.01470961, -1244659.20932869,-1296945.03256045, -39583.1960413812)),
);

/* Setup layers */
$layers = isset($_GET["layers"])? $_GET["layers"]: 
          Array("n0q");
// Make sure layers is an array...
if (gettype($layers) == "string"){
	$layers = Array($layers);
}

/* Straight CGI Butter */
$sector = isset($_GET["sector"]) ? $_GET["sector"] : "iem";
$width = get_int404("width", 640);
$height = get_int404("height", 480);
$lsrbuffer = get_int404("lsrbuffer", 15);

// Now, maybe we set a VTEC string, lets do all sorts of fun
$vtec_limiter = "";
if (isset($_GET["vtec"]))
{
    $cvtec = xssafe($_GET["vtec"]);
    // cull errand _
    $pos = strpos($cvtec, "_");
    if ($pos !== false) {
        $cvtec = substr($cvtec, 0, $pos);
    }
	// we may have gotten here with '-' or '.' in vtec string, rectify
	$cvtec = str_replace("-", ".", strtoupper($cvtec));
  	$tokens = explode(".", $cvtec);
 	if (sizeof($tokens) == 7){
    	list($year, $pclass, $status, $wfo, $phenomena, $significance, 
    		 $eventid) = explode(".", $cvtec);
  	} else {
    	list($year, $wfo, $phenomena, $significance, 
    		 $eventid) = explode(".", $cvtec);
    }
  	$eventid = intval($eventid);
  	$year = intval($year);
  	$wfo = substr($wfo,1,3);
  	// Try to find this warning as a polygon first, then look at warnings table
  	$sql = <<<EOF
  	with one as (
  		SELECT max(issue) as v, max(expire) as e, ST_extent(geom),
  		max('P')::text as gtype
  		from sbw_{$year}
  		WHERE wfo = $1 and phenomena = $2 and eventid = $3 and
  		significance = $4 and status = 'NEW'),
  	two as (
  		SELECT max(issue) as v, max(expire) as e, ST_extent(u.geom),
  		'C'::text as gtype from warnings_{$year} w JOIN ugcs u on (w.gid = u.gid)
  		WHERE w.wfo = $1 and phenomena = $2 and eventid = $3 and
  		significance = $4),
  	agg as (SELECT * from one UNION ALL select * from two)

  	SELECT v, e, ST_xmax(st_extent) as x1, st_xmin(st_extent) as x0,
  	ST_ymax(st_extent) as y1, st_ymin(st_extent) as y0, gtype from agg
  	WHERE gtype is not null LIMIT 1
EOF;
  	$rs = pg_prepare($postgis, "OOR", $sql);
  	$rs = pg_execute($postgis, "OOR", Array($wfo, $phenomena, $eventid,
  			$significance));
	if (pg_num_rows($rs) != 1) exit("ERROR: Unable to find warning!");
  	$row = pg_fetch_assoc($rs, 0); 
  	$lpad = 0.5;
  	$y1 = $row["y1"] +$lpad; $y0 = $row["y0"]-$lpad; 
  	$x1 = $row["x1"] +$lpad; $x0 = $row["x0"]-$lpad;
  	$xc = $x0 + ($row["x1"] - $row["x0"]) / 2;
  	$yc = $y0 + ($row["y1"] - $row["y0"]) / 2;

  	$sector = "custom";
  	$sectors["custom"] = Array("epsg"=> 4326, "ext" => Array($x0,$y0,$x1,$y1));

		// Now the concern here is what to do with the valid time of this plot
		// If now() is less than event end, set the plot time to now
  	$dts = strtotime($row["v"]);
		$dts2 = strtotime($row["e"]);
		if (time() < $dts2){
			$dts = time();
		}

  	$vtec_limiter = sprintf("and phenomena = '%s' and eventid = %s and 
    	significance = '%s' and w.wfo = '%s'", $phenomena, $eventid, 
    	$significance, $wfo);
	if ($row["gtype"] == 'P') {
		$layers[] = 'sbw';
	} else {
		$layers[] = 'cbw';
	}
}
if (isset($_REQUEST['pid']))
{
  $pid = $_REQUEST["pid"];
  $dts = gmmktime(substr($_GET["pid"],8,2), substr($_GET["pid"],10,2), 0,
 substr($_GET["pid"],4,2), substr($_GET["pid"],6,2), substr($_GET["pid"],0,4));
  /* First, we query for a bounding box please */
  $rs = pg_prepare($postgis, "SELECTPID", 
  	"SELECT ST_xmax(ST_extent(geom)) as x1, ST_xmin(ST_extent(geom)) as x0, "
    ."ST_ymin(ST_extent(geom)) as y0, ST_ymax(ST_extent(geom)) as y1 "
    ."from sps WHERE product_id = $1");
  $result = pg_execute($postgis, "SELECTPID", Array($pid));
  $row = pg_fetch_array($result, 0);
  $lpad = 0.5;
  $y1 = $row["y1"] +$lpad; $y0 = $row["y0"]-$lpad;
  $x1 = $row["x1"] +$lpad; $x0 = $row["x0"]-$lpad;
  $xc = $x0 + ($row["x1"] - $row["x0"]) / 2; 
  $yc = $y0 + ($row["y1"] - $row["y0"]) / 2;
  $sector = "custom";
  $sectors["custom"] = Array("epsg"=> 4326, "ext" => Array($x0,$y0,$x1,$y1) );
}

/* Could define a custom box */
if (isset($_GET["bbox"]))
{
  $sector = "custom";
  $bbox = isset($_GET["bbox"]) ? explode(",",$_GET["bbox"]) : die("No BBOX");
  $sectors["custom"] = Array("epsg"=> 4326, "ext" => $bbox);
}
/* Fetch bounds based on wfo as being set by bounds */
if ($sector == "wfo"){
	$sector_wfo = isset($_REQUEST["sector_wfo"]) ? strtoupper($_REQUEST["sector_wfo"]): "DMX";
	/* Fetch the bounds */
	pg_prepare($postgis, "WFOBOUNDS", "SELECT ST_xmax(geom) as xmax, ST_ymax(geom) as ymax, "
	    ." ST_xmin(geom) as xmin, ST_ymin(geom) as ymin from "
		." (SELECT ST_Extent(geom) as geom from ugcs WHERE "
		." wfo = $1 and end_ts is null) as foo");
	$rs = pg_execute($postgis, "WFOBOUNDS", Array($sector_wfo));
	if (pg_numrows($rs) > 0){
		$row = pg_fetch_assoc($rs,0);
		$buffer = 0.25;
		$sectors["wfo"] = Array("epsg" => 4326, 
			"ext" => Array($row["xmin"] - $buffer, $row["ymin"] - $buffer, 
						$row["xmax"] + $buffer, $row["ymax"] + $buffer));
	}
}

/* Lets determine our timestamp.  Our options include
   1.  Specified by URI, $ts
   2.  They specified a VTEC string, use that
   3.  Nothing specified, realtime!
*/
$ts = isset($_GET["ts"]) ? gmmktime(
 substr($_GET["ts"],8,2), substr($_GET["ts"],10,2), 0,
 substr($_GET["ts"],4,2), substr($_GET["ts"],6,2), substr($_GET["ts"],0,4)): 
 time();
$ts1 = isset($_GET["ts1"]) ? gmmktime(
 substr($_GET["ts1"],8,2), substr($_GET["ts1"],10,2), 0,
 substr($_GET["ts1"],4,2), substr($_GET["ts1"],6,2), substr($_GET["ts1"],0,4)): 
 0;
 $ts2 = isset($_GET["ts2"]) ? gmmktime(
 substr($_GET["ts2"],8,2), substr($_GET["ts2"],10,2), 0,
 substr($_GET["ts2"],4,2), substr($_GET["ts2"],6,2), substr($_GET["ts2"],0,4)): 
 0;
if (isset($dts) && ! isset($_GET["ts"])) { $ts = $dts; }
if ($ts1 == 0) { $ts1 = $ts; }
if (isset($dts2) && ! isset($_GET["ts2"])) { $ts2 = $dts2; }
/* Make sure we have a minute %5 */
if (time() - $ts > 300)
{
  $radts = $ts - (intval(date("i", $ts) % 5) * 60);
}

/* Lets Plot stuff already! */


$mapFile = "../../data/gis/base".$sectors[$sector]['epsg'].".map";
$map = ms_newMapObj($mapFile);
$map->setSize($width, $height);
$map->setExtent($sectors[$sector]['ext'][0],
                $sectors[$sector]['ext'][1], 
                $sectors[$sector]['ext'][2],
                $sectors[$sector]['ext'][3]);
if (in_array("n0q", $layers) || in_array("ridge", $layers)){
  $map->selectOutputFormat("png24");
}

$img = $map->prepareImage();

$namerica = $map->getlayerbyname("namerica");
$namerica->set("status", MS_ON);
$namerica->draw($img);

$lakes = $map->getlayerbyname("lakes");
$lakes->set("status", MS_ON);
$lakes->draw($img);

$places = $map->getlayerbyname("places2010");
$places->set("status", in_array("places", $layers) );
$places->draw($img);

if (in_array("goes", $layers) && isset($_REQUEST["goes_sector"]) &&
	isset($_REQUEST["goes_product"])){
		$res = get_goes_fn_and_time($ts, strtoupper($_REQUEST["goes_sector"]), 
										strtoupper($_REQUEST["goes_product"]));
		if ($res[0] != NULL){
			$radar = $map->getlayerbyname("east_vis_1km");
    		$radar->set("status", MS_ON );
    		$radar->set("data", $res[0]);
    		$radar->draw($img);
    		
    		$plotmeta["subtitle"] .= sprintf(" GOES %s %s %s ", 
    			$_REQUEST["goes_sector"], $_REQUEST["goes_product"],
    			strftime("%-2I:%M %p %Z" ,  $res[1]));
		}
}

/* Draw NEXRAD Layer */
if (in_array("nexrad", $layers) || in_array("nexrad_tc", $layers)  || in_array("nexrad_tc6", $layers)){
  $radarfp = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0r_0.tif";
  if (($ts + 300) < time()) {
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0r_%Y%m%d%H%M.png", $radts);
  }
  if (in_array("nexrad_tc", $layers)){
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/max_n0r_0z0z_%Y%m%d.png", $ts);
  }
  if (in_array("nexrad_tc6", $layers)){
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/max_n0r_6z6z_%Y%m%d.png", $ts);
  }
  if (is_file($radarfp)){
    $radar = $map->getlayerbyname("nexrad_n0r");
    $radar->set("status", MS_ON );
    $radar->set("data", $radarfp);
    $radar->draw($img);
  }
}

if (in_array("n0q", $layers) || in_array("n0q_tc", $layers) || in_array("n0q_tc6", $layers)){
  $radarfp = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png";
  if (($ts + 300) < time()) {
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/n0q_%Y%m%d%H%M.png", $radts);
  }
  if (in_array("n0q_tc", $layers)){
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/max_n0q_0z0z_%Y%m%d.png", $ts);
  }
  if (in_array("n0q_tc6", $layers)){
    $radarfp = gmstrftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/max_n0q_6z6z_%Y%m%d.png", $ts);
  }
  if (is_file($radarfp)){
    $radar = $map->getlayerbyname("nexrad_n0q");
    $radar->set("status", MS_ON );
    $radar->set("data", $radarfp);
    $radar->draw($img);
  }
}

if (in_array("ridge", $layers) && isset($_REQUEST["ridge_radar"]) &&
	isset($_REQUEST["ridge_product"])){
		$res = get_ridge_fn_and_time($ts, strtoupper($_REQUEST["ridge_radar"]), 
										strtoupper($_REQUEST["ridge_product"]));
		if ($res[0] != NULL){
			$radar = $map->getlayerbyname("nexrad_n0q");
    		$radar->set("status", MS_ON );
    		$radar->set("data", $res[0]);
    		$radar->draw($img);
    		$plotmeta["subtitle"] .= sprintf(" RIDGE %s %s %s ", 
    			$_REQUEST["ridge_radar"], $_REQUEST["ridge_product"],
    			strftime("%-2I:%M %p %Z" ,  $res[1]));
		}
}


$states = $map->getlayerbyname("states");
$states->set("status", MS_ON);
$states->draw($img);

/* All SBWs for a WFO */
if (in_array("allsbw", $layers) && isset($_REQUEST["sector_wfo"])){
	$sbwh = $map->getlayerbyname("allsbw");
	$sbwh->set("status",  MS_ON);
	$sbwh->set("connection", get_dbconn_str("postgis"));
	//$sbwh->set("maxscale", 10000000);
	$sql = sprintf(
        "geom from (select phenomena, geom, random() as oid from sbw "
	    ."WHERE significance = 'W' and status = 'NEW' and wfo = '%s' and "
	    ."phenomena in ('SV') "
		."and issue > '2007-10-01') as foo "
	    ."using unique oid using SRID=4326", $sector_wfo);
	$sbwh->set("data", $sql);
	$sbwh->draw($img);
}
$counties = $map->getlayerbyname("uscounties");
$counties->set("status", in_array("uscounties", $layers) );
$counties->draw($img);



$cwas = $map->getlayerbyname("cwas");
$cwas->set("status", in_array("cwas", $layers) );
$cwas->draw($img);

/* Buffered LSRs */
if (in_array("bufferedlsr", $layers)){
	$blsr = ms_newLayerObj($map);
	$blsr->setConnectionType( MS_POSTGIS);
	$blsr->set("connection", get_dbconn_str("postgis"));
	$blsr->set("status", in_array("bufferedlsr", $layers) );
	$sql = "geo from (select distinct city, magnitude, valid, "
	  ."ST_Transform(ST_Buffer(ST_Transform(geom,2163),${lsrbuffer}000),4326) as geo, "
	  ."type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
	  ."from lsrs WHERE "
	  ."ST_Overlaps((select geom from sbw_". date("Y", $ts) ." WHERE "
	           ."wfo = '$wfo' and phenomena = '$phenomena' and "
	           ."significance = '$significance' and eventid = $eventid "
	           ."and status = 'NEW' LIMIT 1), "
	     ."ST_Transform(ST_Buffer(ST_Transform(geom,2163),${lsrbuffer}000),4326) "
	           .") and "
	  ."valid >= '". date("Y-m-d H:i", $ts) ."' and "
	  ."valid < '". date("Y-m-d H:i", $ts2) ."' and "
	  ."((type = 'M' and magnitude >= 34) or "
	         ."(type = 'H' and magnitude >= 0.75) or type = 'W' or "
	         ."type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D' "
	         ."or type = 'F') ORDER by valid DESC) as foo "
	  ."USING unique k USING SRID=4326";
	$blsr->set("data", $sql);
	$blsr->set("type", MS_LAYER_POLYGON);
	$blsr->setProjection("init=epsg:4326");
	$blc0 = ms_newClassObj($blsr);
	$blc0->set("name", "Buffered LSRs (${lsrbuffer} km)");
	$blc0s0 = ms_newStyleObj($blc0);
	$blc0s0->set("symbolname", 'circle');
	$blc0s0->color->setRGB(0,0,0);
	$blc0s0->backgroundcolor->setRGB(0,180,120);
	$blc0s0->outlinecolor->setRGB(50,50,50);
	$blsr->draw($img);
}

/* Watch by County */
$wbc = $map->getlayerbyname("watch_by_county");
$wbc->set("status", in_array("watch_by_county", $layers) );
$wbc->set("connection", get_dbconn_str("postgis"));
$sql = sprintf("g from (select phenomena, eventid, ".
		"ST_buffer(ST_collect(u.simple_geom), 0) as g ".
		"from warnings w JOIN ugcs u ".
		"on (u.gid = w.gid) WHERE ".
		"significance = 'A' and phenomena IN ('TO','SV') and ".
		"issue <= '%s:00+00' and expire > '%s:00+00' ".
		"GROUP by phenomena, eventid ORDER by phenomena ASC) as foo ".
		"using SRID=4326 using unique phenomena",
  gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts) );
$wbc->set("data", $sql);
$wbc->draw($img);

$watches = $map->getlayerbyname("watches");
$watches->set("status", in_array("watches", $layers) );
$watches->set("connection", get_dbconn_str("postgis"));
$sql = sprintf("geom from (select type as wtype, geom, num from watches "
       ."WHERE issued <= '%s:00+00' and expired > '%s:00+00') as foo "
	   ."using SRID=4326 using unique num", 
       gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts));
$watches->set("data", $sql );
$watches->draw($img);

/* Plot the warning explicitly */
if (isset($_REQEST["pid"]))
{
  $wc = ms_newLayerObj($map);
  $wc->setConnectionType( MS_POSTGIS );
  $wc->set("connection", get_dbconn_str("postgis"));
  $wc->set("status", MS_ON );
  $sql = sprintf("geom from (select geom, product_id from sps "
  		."WHERE product_id = '$pid') as foo using unique product_id using SRID=4326");
  $wc->set("data", $sql);
  $wc->set("type", MS_LAYER_LINE);
  $wc->setProjection("init=epsg:4326");

  $wcc0 = ms_newClassObj($wc);
  $wcc0->set("name", "Product");
  $wcc0s0 = ms_newStyleObj($wcc0);
  $wcc0s0->color->setRGB(255,0,0);
  $wcc0s0->set("size", 3);
  $wcc0s0->set("symbolname", 'circle');
  $wc->draw($img);
}


// Draws the county-based VTEC warning, only if "cbw" in $layers
if (isset($_REQUEST["vtec"]) && in_array("cbw", $layers))
{
  $wc = ms_newLayerObj($map);
  $wc->setConnectionType(MS_POSTGIS);
  $wc->set("connection", get_dbconn_str("postgis"));
  $wc->set("status", MS_ON);
  $sql = sprintf("geom from (select eventid, w.wfo, significance, "
  		."phenomena, u.geom, random() as oid from warnings_$year w JOIN ugcs u "
  		."on (u.gid = w.gid) WHERE w.wfo = '$wfo' "
  		."and phenomena = '$phenomena' and significance = '$significance' "
  		."and eventid = $eventid ORDER by phenomena ASC) as foo "
  		."using unique oid using SRID=4326");
  $wc->set("data", $sql);
  $wc->set("type", MS_LAYER_LINE);
  $wc->setProjection("init=epsg:4326");

  $wcc0 = ms_newClassObj($wc);
  $wcc0->set("name", $vtec_phenomena[$phenomena] ." ". $vtec_significance[$significance] );
  $wcc0s0 = ms_newStyleObj($wcc0);
  $wcc0s0->color->setRGB(255,0,0);
  $wcc0s0->set("width", 3);
  $wcc0s0->set("symbol", 'circle');
  $wc->draw($img);
  
}

/* Storm based warning history, plotted as a white outline, I think */
if (in_array("sbwh", $layers) && intval(gmstrftime("%Y",$ts)) > 2001){
	$ptext = "'ZZ' as phenomena";
	$sbwh = $map->getlayerbyname("sbw");
	$sbwh->set("status", MS_ON);
	$sbwh->set("connection", get_dbconn_str("postgis"));
	//$sbwh->set("maxscale", 10000000);
	$sql = sprintf(
        "geom from (select %s, geom, random() as oid from sbw_%s w "
	    ."WHERE significance != 'A' and polygon_begin <= '%s:00+00' and "
	    ."polygon_end > '%s:00+00' "
	    ."%s) as foo using unique oid using SRID=4326", 
	    $ptext, gmstrftime("%Y",$ts),
	    gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts),
	    $vtec_limiter );
	$sbwh->set("data", $sql);
	$sbwh->draw($img);
}



/* Storm Based Warning */
if (in_array("sbw", $layers)  && intval(gmstrftime("%Y",$ts)) > 2001){
	$ptext = "phenomena";
	if (in_array("sbw", $layers) && in_array("cbw", $layers))
	{
	  $ptext = "'ZZ' as phenomena";
	}
	$sbw = $map->getlayerbyname("sbw");
	$sbw->set("status", MS_ON);
	$sbw->set("connection", get_dbconn_str("postgis"));
	//$sbw->set("maxscale", 10000000);
	$sql = sprintf("geom from (select %s, geom, random() as oid from sbw_%s w "
	    ."WHERE significance != 'A' and polygon_begin <= '%s:00+00' "
		."and polygon_end > '%s:00+00' "
	    ."%s) as foo using unique oid using SRID=4326", 
	    $ptext, gmstrftime("%Y",$ts),
	    gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts),
	    $vtec_limiter );
	$sbw->set("data", $sql);
	$sbw->draw($img);
}

/* warnings by county */
$w0c = $map->getlayerbyname("warnings0_c");
$w0c->set("connection", get_dbconn_str("postgis"));
$w0c->set("status", in_array("county_warnings", $layers) );
$sql = sprintf("geom from (select u.geom, phenomena, significance, "
		."random() as oid from warnings_%s w JOIN ugcs u on (u.gid = w.gid) "
		."WHERE issue <= '%s:00+00' and expire > '%s:00+00' %s "
		."ORDER by phenomena ASC) as foo using unique oid using SRID=4326", 
    gmstrftime("%Y",$ts),
    gmstrftime("%Y-%m-%d %H:%M", $ts), gmstrftime("%Y-%m-%d %H:%M", $ts),
    $vtec_limiter );
$w0c->set("data", $sql);
$w0c->draw($img);

/* Local Storm Reports */
$lsrs = $map->getlayerbyname("lsrs");
$lsrs->set("connection", get_dbconn_str("postgis"));
$lsrs->set("status",in_array("lsrs", $layers) );
if ($ts2 > $ts1){
 $sql = "geom from (select distinct city, magnitude, valid, geom, "
 		."type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
 		."from lsrs WHERE "
 		."valid >= '". gmstrftime("%Y-%m-%d %H:%M", $ts1) .":00+00' and "
 		."valid < '". gmstrftime("%Y-%m-%d %H:%M", $ts2) .":00+00' "
 		."ORDER by valid DESC) as foo USING unique k USING SRID=4326";
} else {
 $sql = "geom from (select distinct city, magnitude, valid, geom, "
 		."type as ltype, city || magnitude || ST_x(geom) || ST_y(geom) as k "
 		."from lsrs WHERE "
 		."valid = '". gmstrftime("%Y-%m-%d %H:%M", $ts) .":00+00') as foo "
 		."USING unique k USING SRID=4326";
}
$lsrs->set("data", $sql);
$lsrs->draw($img);

/* County Intersection */
if (in_array("ci", $layers) ){
	$ci = ms_newLayerObj($map);
	$ci->setConnectionType( MS_POSTGIS);
	$ci->set("connection", get_dbconn_str("postgis"));
	$ci->set("status", in_array("ci", $layers) );
	$tblyr = date("Y", $ts);
	$sql = <<<EOF
geo from (
	WITH stormbased as (SELECT geom from sbw_$tblyr where wfo = '$wfo' 
		and eventid = $eventid and significance = '$significance' 
		and phenomena = '$phenomena' and status = 'NEW'), 
	countybased as (SELECT ST_Union(u.geom) as geom from 
		warnings_$tblyr w JOIN ugcs u on (u.gid = w.gid) 
		WHERE w.wfo = '$wfo' and eventid = $eventid and 
		significance = '$significance' and phenomena = '$phenomena') 
				
	SELECT ST_SetSRID(ST_intersection(
	      ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
	      ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
	   ), 4326) as geo,
	random() as k
	from stormbased s, countybased c
			
) as foo USING unique k USING SRID=4326
EOF;
	$ci->set("data", $sql);
	$ci->set("type", MS_LAYER_LINE);
	$ci->setProjection("init=epsg:4326");
	$cic0 = ms_newClassObj($ci);
	$cic0->set("name", "County Intersection");
	$cic0s0 = ms_newStyleObj($cic0);
	//$cic0s0->set("symbolname", 'circle');
	$cic0s0->color->setRGB(250,0,250);
	$cic0s0->set("width", 5);
	$ci->draw($img);
}

/* Interstates */
$interstates = $map->getlayerbyname("interstates");
$interstates->set("status", in_array("interstates", $layers) );
$interstates->draw($img);

/* roads */
$roads = $map->getlayerbyname("roads");
$roads->set("connection", get_dbconn_str("postgis"));
$roads->set("status", in_array("roads", $layers) );
$roads->draw($img);

/* roads */
$roadsint = $map->getlayerbyname("roads-inter");
$roadsint->set("connection", get_dbconn_str("postgis"));
$roadsint->set("status", in_array("roads-inter", $layers) );
$roadsint->draw($img);

if (in_array("usdm", $layers)){
	$usdm = $map->getlayerbyname("usdm");
	$usdm->set("status", MS_ON );
	$usdm->draw($img);
}

if (in_array("cities", $layers)){
	$l = $map->getlayerbyname("cities");
	$l->set("status", MS_ON );
	$l->draw($img);
}

if (in_array("surface", $layers)){
	$surface = $map->getlayerbyname("surface");
	$surface->set("status", MS_ON );
	$surface->draw($img);
}
if (in_array("airtemps", $layers)){
	$airtemps = $map->getlayerbyname("airtemps");
	$airtemps->set("status", MS_ON );
	if ($width > 800){
		for ($i=0;$i<$airtemps->numclasses;$i++){
			$cl = $airtemps->getClass($i);
			$cllabel = $cl->getLabel(0);
			$cllabel->set("size", 20);
		}
	}
	$airtemps->draw($img);
}

$tlayer = $map->getLayerByName("bar640t-title");
$point = ms_newpointobj();
$point->setXY(80, 9);
$tzformat = "%d %B %Y %-2I:%M %p %Z";
if (isset($_REQUEST["tz"])) {
	$tz = $_REQUEST["tz"];
	if ($tz == 'MDT' || $tz == 'MST'){
		$tz = "America/Denver";
	}
	elseif ($tz == 'PDT' || $tz == 'PST'){
		$tz = "America/Los_Angeles";
	}
	elseif ($tz == 'CDT' || $tz == 'CST'){
		$tz = "America/Chicago";
	}
	elseif ($tz == 'EDT' || $tz == 'EST'){
		$tz = "America/New_York";
	}
	date_default_timezone_set($tz); 
	if ($_REQUEST["tz"] == 'UTC'){
		$tzformat = "%d %B %Y %H:%M %Z";
	}
}
$d = strftime($tzformat ,  $ts); 
if (isset($_GET["title"])){
  $title = substr($_GET["title"],0,100);
} else if ( isset($_GET["vtec"]) ){
  $title = "VTEC ID: ". $_GET["vtec"];
} else if (in_array("nexrad", $layers)){
  $title = "NEXRAD Base Reflectivity";
} else if (in_array("n0q", $layers)){
  $title = "NEXRAD Base Reflectivity";
} else if (in_array("n0q_tc", $layers)){
  $title = "IEM NEXRAD Daily N0Q Max Base Reflectivity";
  $d = sprintf("Valid between %s 00:00 and 23:59 UTC",
      gmdate("d M Y", $ts));
} else if (in_array("n0q_tc6", $layers)){
  $title = "IEM NEXRAD 24 Hour N0Q Max Base Reflectivity";
  $d = sprintf("Valid between %s 06:00 and %s 05:55 UTC",
        gmdate("d M Y", $ts), gmdate("d M Y", $ts + 86400));
} else if (in_array("nexrad_tc", $layers)){
  $title = "IEM NEXRAD Daily N0R Max Base Reflectivity";
  $d = sprintf("Valid between %s 00:00 and 23:59 UTC",
      gmdate("d M Y", $ts));
} else if (in_array("nexrad_tc6", $layers)){
    $title = "IEM NEXRAD 24 Hour N0R Max Base Reflectivity";
    $d = sprintf("Valid between %s 06:00 and %s 05:55 UTC",
        gmdate("d M Y", $ts), gmdate("d M Y", $ts + 86400));
} else {
  $title = "IEM Plot";
  if ($plotmeta["subtitle"] != ""){
  	$title = $plotmeta["subtitle"];
  	$plotmeta["subtitle"] = "";
  }
}

$header_height = ($plotmeta["subtitle"] == "")? 36: 53;
draw_header($map, $img, $width, $header_height);

$point->draw($map, $tlayer, $img, 0, $title);

$point = ms_newpointobj();
$point->setXY(80, 26);
$point->draw($map, $tlayer, $img, 1,"$d");
if ($plotmeta["subtitle"] != ""){
	$point = ms_newpointobj();
	$point->setXY(80, 43);
	$point->draw($map, $tlayer, $img, 1, $plotmeta["subtitle"]);
}

$map->drawLabelCache($img);

$layer = $map->getLayerByName("logo");
$point = ms_newpointobj();
$point->setXY(42, 32);
$point->draw($map, $layer, $img, 0);

if (in_array("nexrad", $layers) || in_array("nexrad_tc", $layers) || in_array("nexrad_tc6", $layers)){
  $layer = $map->getLayerByName("n0r-ramp");
  $point = ms_newpointobj();
  $point->setXY(($width - 80), 15);
  $point->draw($map, $layer, $img, 0);
}
if (in_array("n0q", $layers) || in_array("n0q_tc", $layers) || in_array("n0q_tc6", $layers)){
  $layer = $map->getLayerByName("n0q-ramp");
  $point = ms_newpointobj();
  $point->setXY(($width - 130), 18);
  $point->draw($map, $layer, $img, 0);
}

if (in_array("legend", $layers)){
  $map->embedLegend($img);
}
//$map->drawLabelCache($img);
//$map->save("/tmp/test.map");

header("Content-type: image/png");
$img->saveImage('');

$map->free();
unset($map);
