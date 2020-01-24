<?php
/* cow.php
 *  Functionized routines for IEM Cow
 *  This way we can call from other applications, like dailyb :)
 */
putenv("TZ=UTC");

class cow {

function __construct($dbconn){
    /* Constructor */
    $this->dbconn = $dbconn;
    pg_query($dbconn, "SET TIME ZONE 'UTC'");

    $this->wfo = Array();        /* Array of WFOs to potentially limit */
    $this->warnings = Array();   /* Array of warnings */
    $this->lsrs = Array();       /* Array of LSRs */
    $this->sts = 0;              /* Verification window start UTC */
    $this->ets = 0;              /* Vertification window end UTC */
    $this->wtype = Array();      /* VTEC Phenomena types to verify */
    $this->ltype = Array();      /* LSR Types to verify with */
    $this->hailsize = 0.75;      /* Hail size limitation */
    $this->lsrbuffer = 15;       /* LSR report buffer in km */
    $this->warningbuffer = 0.01;   // Buffer warnings by this number of degrees
    $this->wind = 58;			/* Wind threshold in mph */
    $this->useWindHailTag = false;  /* Option to use wind hail tag to verify */
    $this->limitwarns = false;  /* Limit listed warnings to wind and hail criterion */
	$this->fcster = ''; // allowing for filtering based on product signature
}

/* Standard Workflow */
function milk(){ 
    $this->loadWarnings();
    $this->loadLSRs();
    $this->computeSharedBorder();
    $this->sbwVerify();
    $this->areaVerify();
}

function callDB($sql){
    $rs = @pg_query($this->dbconn, $sql);
    //if (! $rs ){ echo $sql; }
    return $rs;
}

function setForecaster($s){
	$this->fcster = $s;
}
function sqlForecasterBuilder(){
	if ($this->fcster == '') {
		return '';
	}
	return sprintf(" and fcster = '%s' ", $this->fcster);
}
function setWarningBuffer($b){
	$this->warningbuffer = $b;
}
function setLSRBuffer($buffer){
    $this->lsrbuffer = $buffer;
}

function setLimitWFO($arWFO){
    $this->wfo = $arWFO;
}

function setLimitTime($sts, $ets){
    $this->sts = $sts;
    $this->ets = $ets;
}

function setLimitType($arType){
    $this->wtype = $arType;
}

function setLimitLSRType($arType){
    $this->ltype = $arType;
}

function setHailSize($val){
    $this->hailsize = $val;
}
function setWind($val){
    $this->wind = $val;
}

function sqlWFOBuilder(){
    reset($this->wfo);
    if (sizeof($this->wfo) == 0){ return "1 = 1"; }

    $sql = "w.wfo IN ('". implode(",", $this->wfo) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function sqlLSRTypeBuilder(){
    reset($this->ltype);
    if (sizeof($this->ltype) == 0){ return "type in ('@')"; }
    $l = Array();
    foreach($this->ltype as $k => $v){
        if ($v == "TO"){ $l[] = "T"; }
        else if ($v == "SV"){ $l[] = "H"; $l[] = "G"; $l[] = "D"; }
        else if ($v == "MA"){ $l[] = "M"; $l[] = "W"; }
        else if ($v == "FF"){ $l[] = "F"; $l[] = 'x';}
        else if ($v == "DS"){ $l[] = "2"; }
        else{ $l[] = $v; }
    }   
    $sql = "type IN ('". implode(",", $l) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function sqlTypeBuilder(){
    if (sizeof($this->wtype) == 0) return "w.phenomena IN ('ZZ')";

    $sql = "phenomena IN ('". implode(",", $this->wtype) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function computeAverageSize(){
    if (sizeof($this->warnings) == 0){ return 0; }
    reset($this->warnings);
    $polysz = 0;
    foreach($this->warnings as $k => $v){
        $polysz += $v["parea"];
    }
    return $polysz / floatval(sizeof($this->warnings));
}

function computeSizeReduction(){
    reset($this->warnings);
    $polysz = 0;
    $countysz = 0;
    foreach($this->warnings as $k => $v){
        $polysz += $v["parea"];
        $countysz += $v["carea"];
    }
    if ($countysz == 0){ return 0; }
    return ($countysz - $polysz) / $countysz * 100.0;
}

function computeUnwarnedEvents(){
    return sizeof($this->lsrs) - $this->computeWarnedEvents();
}


function computeWarnedEvents(){
    if (sizeof($this->lsrs) == 0){ return 0; }

    reset($this->lsrs);
    $counter = 0;
    foreach($this->lsrs as $k => $v){
        if ($v["warned"]){ $counter += 1; }
    }
    return $counter;
}

function computeTDQEvents(){
    if (sizeof($this->lsrs) == 0){ return 0; }

    reset($this->lsrs);
    $counter = 0;
    foreach($this->lsrs as $k => $v){
        if ($v["tdq"]){ $counter += 1; }
    }
    return $counter;
}

function computeMaxLeadTime(){
   if (sizeof($this->lsrs) == 0){ return 0; }

   $large = 0;
   reset($this->lsrs);
   foreach($this->lsrs as $k => $v){
       if ($v["leadtime"] > $large){ $large = $v["leadtime"]; }
   }
   return $large;
}
function computeMinLeadTime(){
   if (sizeof($this->lsrs) == 0){ return 0; }
   $smallest = 99;
   reset($this->lsrs);
   foreach($this->lsrs as $k => $v){
       if ($v["leadtime"] < $smallest){ $smallest = $v["leadtime"]; }
   }
   return $smallest;
}


function computeAllLeadTime(){
   $ar = Array();
   reset($this->lsrs);
   foreach($this->lsrs as $k => $v){
       if ($v["leadtime"] != "NA"){ $ar[] = $v["leadtime"]; }
   }
   if (sizeof($ar) == 0){ return 0; }
   return array_sum($ar) / floatval( sizeof($ar) );
}

function computeAverageLeadTime(){
   $ar = Array();
   reset($this->warnings);
   foreach($this->warnings as $k => $v){
       if ($v["lead0"] > -1){ $ar[] = $v["lead0"]; }
   }
   if (sizeof($ar) == 0){ return 0; }
   return array_sum($ar) / floatval( sizeof($ar) );
}

function computeAveragePerimeterRatio(){
   $shared = 0;
   $total = 0;
   reset($this->warnings);
   foreach($this->warnings as $k => $v){
       $shared += $v["sharedborder"];
       $total += $v["perimeter"];
   }
   if ($total == 0) return 0;
   return ($shared / $total * 100.0);
}

function computeCSI(){
   $pod = $this->computePOD();
   $far = $this->computeFAR();
   return pow((pow($pod,-1) + pow(1-$far,-1) - 1), -1);
}

function computePOD(){
   $a_e = $this->computeWarnedEvents();
   $b = sizeof($this->lsrs) - $a_e;
   if ($b + $a_e == 0){ return 0; }
   return floatval($a_e) / floatval( $a_e + $b );
}

function computeFAR(){
    $a_w = $this->computeWarningsVerified();
    $c = sizeof($this->warnings) - $a_w;
    if ($c + $a_w == 0){ return 0; }
    return floatval($c) / floatval( $a_w + $c );
}

function computeAreaVerify(){
    $polysz = 0;
    $lsrsz = 0;
    if (sizeof($this->warnings) == 0){ return 0; }
    reset($this->warnings);
    foreach($this->warnings as $k => $v){
    	if ($v["buffered"] === null) continue;
        $polysz += $v["parea"];
        $lsrsz += $v["buffered"];
    }
    return $lsrsz / $polysz * 100.0;

}

function computeWarningsVerifiedPercent(){
    if (sizeof($this->warnings) == 0){ return 0; }
    return $this->computeWarningsVerified() / floatval(sizeof($this->warnings)) * 100.0;
}

function computeWarningsVerified(){
    reset($this->warnings);
    $counter = 0;
    foreach($this->warnings as $k => $v){
        if ($v["verify"]){ $counter += 1; }
    }
    return $counter;
}

function computeWarningsUnverified(){
    return sizeof($this->warnings) - $this->computeWarningsVerified();
}

function computeSharedBorder(){
	// Compute the storm based warning intersection with the counties
    reset($this->warnings);
    foreach($this->warnings as $k => $v){
    	$sql = <<<EOF
    WITH stormbased as (SELECT geom from sbw_{$v["year"]} 
    	where wfo = '{$v["wfo"]}' 
		and eventid = {$v["eventid"]} and significance = '{$v["significance"]}' 
		and phenomena = '{$v["phenomena"]}' and status = 'NEW'), 
	countybased as (SELECT ST_Union(ST_Buffer(u.simple_geom, 0)) as geom from 
		warnings_{$v["year"]} w JOIN ugcs u on (u.gid = w.gid) 
		WHERE w.wfo = '{$v["wfo"]}' and eventid = {$v["eventid"]} and 
		significance = '{$v["significance"]}' and phenomena = '{$v["phenomena"]}') 
				
	SELECT sum(ST_Length(ST_transform(geo,2163))) as s from
		(SELECT ST_SetSRID(ST_intersection(
	      ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
	      ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
	   	 ), 4326) as geo
	from stormbased s, countybased c) as foo
EOF;
    	$rs = $this->callDB($sql);
        if ($rs && pg_num_rows($rs) > 0){
            $row = pg_fetch_array($rs,0);
            $this->warnings[$k]["sharedborder"] = $row["s"];
        } else {
            $this->warnings[$k]["sharedborder"] = 0;
        }
    }
}

function sqlTagLimiter(){
	if ($this->limitwarns){
		return sprintf(" and ((w.windtag >= %s or w.hailtag >= %s) or (w.windtag is null and w.hailtag is null))", $this->wind, $this->hailsize);
	}
	return "";
}

function loadWarnings(){
	/*
	 * Load the warnings stored in the database based on our specifications
	 */
	$sql = sprintf("
	WITH stormbased as (
      SELECT 
		wfo, phenomena, eventid, hailtag, windtag, 
		ST_AsText(geom) as tgeom, significance,
		ST_area(ST_transform(geom,2163)) / 1000000.0 as parea,
		ST_perimeter(ST_transform(geom,2163)) as perimeter,
		ST_xmax(geom) as lon0, ST_ymax(geom) as lat0,
		extract(year from issue at time zone 'UTC') as year
			from sbw w WHERE status = 'NEW' and %s and significance = 'W' and
			issue >= '%s' and issue < '%s' and expire < '%s'
			and %s %s
                
    ), countybased as (
      SELECT  
		w.wfo, phenomena, eventid, significance, 
		max(w.status) as statuses,
		string_agg(u.ugc, ',') as ar_ugc,
		string_agg(u.name ||' '||u.state, '|') as ar_ugcname,
		sum(ST_area(ST_transform(u.geom,2163)) / 1000000.0) as carea,
		min(issue) as missue,
		max(expire) as mexpire,
		extract(year from issue at time zone 'UTC') as year, w.fcster
		from warnings w JOIN ugcs u on (u.gid = w.gid) WHERE           
        w.gid is not null and %s and significance = 'W' and
		issue >= '%s' and issue < '%s' and expire < '%s' 
		and %s %s
		GROUP by w.wfo, phenomena, eventid, significance, year, fcster
    )
	SELECT  
		s.year, s.wfo, s.phenomena, s.eventid, s.tgeom, c.missue as issue, 
			c.mexpire as expire, c.statuses, c.fcster,
			s.significance, s.hailtag, s.windtag, c.carea, c.ar_ugc,
			s.lat0, s.lon0, s.perimeter, s.parea, c.ar_ugcname
			from stormbased s JOIN countybased c on 
			(c.eventid = s.eventid and c.wfo = s.wfo and c.year = s.year
			and c.phenomena = s.phenomena and c.significance = s.significance)
			ORDER by issue ASC
	",  $this->sqlWFOBuilder(), date("Y/m/d H:i", $this->sts), 
	date("Y/m/d H:i", $this->ets), date("Y/m/d H:i", $this->ets), 
	$this->sqlTypeBuilder(), $this->sqlTagLimiter(),
	$this->sqlWFOBuilder(), date("Y/m/d H:i", $this->sts), 
	date("Y/m/d H:i", $this->ets),  date("Y/m/d H:i", $this->ets),
    $this->sqlTypeBuilder(), $this->sqlForecasterBuilder());
	
	//die("<pre>$sql</pre>");
	$rs = $this->callDB($sql);
	
    for ($i=0;$row = pg_fetch_assoc($rs);$i++){
        $key = sprintf("%s-%s-%s-%s", $row["year"], $row["wfo"], 
                       $row["phenomena"], $row["eventid"]);

        $this->warnings[$key] = Array();
        $this->warnings[$key]["lead0"] = -1;
        $this->warnings[$key]["buffered"] = 0;
        $this->warnings[$key]["verify"] = FALSE;
        $this->warnings[$key]["status"] = $row["statuses"];
        $this->warnings[$key]['lsrs'] = Array();
        
        $this->warnings[$key]["hailtag"] = $row["hailtag"];
        $this->warnings[$key]["windtag"] = $row["windtag"];
        $this->warnings[$key]["issue"] = $row["issue"];
        $this->warnings[$key]["phenomena"] = $row["phenomena"];
        $this->warnings[$key]["wfo"] = $row["wfo"];
        $this->warnings[$key]["significance"] = $row["significance"];        
        $this->warnings[$key]["carea"] = $row["carea"];        
        $this->warnings[$key]["lat0"] = $row["lat0"];
        $this->warnings[$key]["lon0"] = $row["lon0"];
        $this->warnings[$key]["sts"] = strtotime($row["issue"]);
        $this->warnings[$key]["ets"] = strtotime($row["expire"]);
        $this->warnings[$key]["expire"] = strtotime($row["expire"]);
        $this->warnings[$key]["eventid"] = $row["eventid"];
        $this->warnings[$key]["year"] = $row["year"];
        $this->warnings[$key]["geom"] = $row["tgeom"];
        $this->warnings[$key]["perimeter"] = $row["perimeter"];
        $this->warnings[$key]["parea"] = $row["parea"];
        $this->warnings[$key]["ugc"] = explode(",",$row["ar_ugc"]);
        $this->warnings[$key]["ugcname"] = explode("|",$row["ar_ugcname"]);
        $this->warnings[$key]["fcster"] = $row["fcster"];
    } /* End of rs for loop */

} /* End of loadWarnings() */

function loadLSRs() {
	/*
	 * Load LSRs from the database using a distinct on what eventually will 
	 * become the primary key for the memory storage
	 */
    $sql = sprintf("SELECT distinct *, ST_x(geom) as lon0, ST_y(geom) as lat0, 
        	ST_astext(geom) as tgeom,
        	ST_astext(ST_buffer( ST_transform(geom,2163), %s000)) as buffered
        	from lsrs w WHERE %s and 
        	valid >= '%s' and valid < '%s' and %s and
        	((type = 'M' and magnitude >= 34) or type = '2' or
         	(type = 'H' and magnitude >= %s) or type = 'W' or
         	type = 'T' or (type = 'G' and magnitude >= %s) or type = 'D'
         	or type = 'F' or type = 'x') ORDER by valid ASC", 
    		$this->lsrbuffer, $this->sqlWFOBuilder(), 
        	date("Y/m/d H:i", $this->sts), date("Y/m/d H:i", $this->ets), 
        	$this->sqlLSRTypeBuilder(), $this->hailsize, $this->wind);
    $rs = $this->callDB($sql);
    for ($i=0;$row = pg_fetch_assoc($rs);$i++)
    {
        $key = sprintf("%s-%s-%s-%s-%s", $row["wfo"], $row["valid"], 
        				$row["type"], $row["magnitude"], $row["city"]);
        $this->lsrs[$key] = $row;
        $this->lsrs[$key]['geom'] = $row["tgeom"];
        $this->lsrs[$key]["ts"] = strtotime($row["valid"]);
        $this->lsrs[$key]["warned"] = False;
        $this->lsrs[$key]["tdq"] = False; /* Tornado DQ */
        $this->lsrs[$key]["leadtime"] = "NA";
        $this->lsrs[$key]["remark"] = $row["remark"];
    }
} /* End of loadLSRs() */

function areaVerify() {
	/*
	 * Compute the areal verification for each warning
	 */
    reset($this->warnings);
    foreach($this->warnings as $wkey => $warn) {
        if (sizeof($warn["lsrs"]) == 0){ 
        	continue; 
        }
        
        $bufferedArray = Array();
        reset($warn["lsrs"]);
        foreach($warn["lsrs"] as $lkey => $lsr){
            $bufferedArray[] = sprintf("ST_SetSRID(ST_GeomFromText('%s'),2163)", 
              $this->lsrs[$lsr]["buffered"]);
        }
        
        $sql = sprintf("SELECT ST_Area(
         			ST_Intersection( ST_Union(ARRAY[%s]), 
                          ST_Transform(ST_GeomFromEWKT('SRID=4326;%s'),2163) ) 
         			) / 1000000.0 as area",
         			implode(",", $bufferedArray), $warn["geom"] );
        $rs = $this->callDB($sql);
        if ($rs === FALSE){ // PostGIS likely threw an error!
        	$row = Array("area" => null);
        } else {
            $row = pg_fetch_array($rs,0);
        }
        $this->warnings[$wkey]["buffered"] = $row["area"];
    }
} // end areaVerify()

function getVerifyHailSize($warn){
	if ($this->useWindHailTag && $warn['hailtag'] != null && $warn['hailtag'] >= $this->hailsize){
		return $warn['hailtag'];
	}
	return $this->hailsize;
}
function getVerifyWind($warn){
	if ($this->useWindHailTag && $warn['windtag'] != null && $warn['windtag'] > $this->wind){
		return $warn['windtag'];
	}
	return $this->wind;
}

function sbwVerify() {
	/*
	 * Compute if a warning verifies or not!
	 */
    reset($this->warnings);
    foreach($this->warnings as $k => $v) {
    	/*
    	 * No SBW found?
    	 */
    	if (!array_key_exists('expire',$v)){
    		continue;
    	}
        /* Look for LSRs! */
        $sql = sprintf("SELECT distinct *
         from lsrs w WHERE 
         geom && ST_Buffer(ST_SetSrid(ST_GeometryFromText('%s'),4326), %s) and 
         ST_contains(ST_Buffer(ST_SetSrid(ST_GeometryFromText('%s'),4326), %s), geom) 
         and %s and wfo = '%s' and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= %s) or type = 'W' or type = '2' or
         type = 'T' or (type = 'G' and magnitude >= %s) or type = 'D'
         or type = 'F' or type = 'x')
         and valid >= '%s+00' and valid <= '%s+00' 
         ORDER by valid ASC", 
         $v["geom"], $this->warningbuffer, 
        		$v["geom"], $this->warningbuffer, $this->sqlLSRTypeBuilder(), 
         $v["wfo"], $this->getVerifyHailSize($v), $this->getVerifyWind($v),
         date("Y/m/d H:i", strtotime($v["issue"])),
         date("Y/m/d H:i", $v["expire"]) );
        $rs = $this->callDB($sql);
        for ($i=0;$row=pg_fetch_assoc($rs);$i++){
            $key = sprintf("%s-%s-%s-%s-%s", 
                   $row["wfo"], $row["valid"], $row["type"],
                   $row["magnitude"], $row["city"]);
            $verify = False;
            if ($v["phenomena"] == "FF"){
                if ($row["type"] == "F" || $row["type"] == 'x') { 
                	$verify = True;
                }
            }
            else if ($v["phenomena"] == "TO"){
                if ($row["type"] == "T") { $verify = True; }
                else { $this->lsrs[$key]["tdq"] = True; }
            }
            else if ($v["phenomena"] == "DS"){
                if ($row["type"] == "2") { $verify = True; }
            }
            else if ($v["phenomena"] == "MA"){
                if ($row["type"] == "W") { $verify = True; }
                else if ($row["type"] == "M") { $verify = True; }
                else if ($row["type"] == "H") { $verify = True; }
            }
            else if ($v["phenomena"] == "SV"){
                if ($row["type"] == "G") { $verify = True; }
                else if ($row["type"] == "D") { $verify = True; }
                else if ($row["type"] == "H") { $verify = True; }
            }
            if ($verify){
                $this->warnings[$k]["verify"] = True;
            }
            /*
             * Sometimes this happens, but not sure why
             */
            if (! array_key_exists($key, $this->lsrs)){
            	continue;
            }
            if (($verify || $this->lsrs[$key]["tdq"]) &&
                 ! $this->lsrs[$key]["warned"] ){
            	$this->lsrs[$key]["warned"] = True;
            	$this->warnings[$k]["lsrs"][] = $key;
            	$this->lsrs[$key]["leadtime"] = ($this->lsrs[$key]["ts"] - 
                       $v["sts"]) / 60;
                if ($this->warnings[$k]["lead0"] < 0){
               $this->warnings[$k]["lead0"] = $this->lsrs[$key]["leadtime"];
                }
            }
        } /* End of loop over found LSRs */

    } /* End of loop over warnings */
}

} /* End of class cow */
?>
