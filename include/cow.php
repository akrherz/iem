<?php
/* cow.php
 *  Functionized routines for IEM Cow
 *  This way we can call from other applications, like dailyb :)
 */
putenv("TZ=GMT");

class cow {

function cow($dbconn){
    /* Constructor */
    $this->dbconn = $dbconn;
    pg_query($dbconn, "SET TIME ZONE 'GMT'");

    $this->wfo = Array();        /* Array of WFOs to potentially limit */
    $this->warnings = Array();   /* Array of warnings */
    $this->lsrs = Array();       /* Array of LSRs */
    $this->sts = 0;              /* Verification window start UTC */
    $this->ets = 0;              /* Vertification window end UTC */
    $this->wtype = Array();      /* VTEC Phenomena types to verify */
    $this->ltype = Array();      /* LSR Types to verify with */
    $this->ugcCache = Array();   /* UGC information */
    $this->hailsize = 0.75;      /* Hail size limitation */
    $this->lsrbuffer = 15;       /* LSR report buffer in km */
}

/* Standard Workflow */
function milk(){ 
    $this->loadWarnings();
    $this->loadLSRs();
    $this->computeUGC();
    $this->computeSharedBorder();
    $this->sbwVerify();
    $this->areaVerify();
}

function callDB($sql){
    $rs = @pg_query($this->dbconn, $sql);
    //if (! $rs ){ echo $sql; }
    return $rs;
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

function sqlWFOBuilder(){
    reset($this->wfo);
    if (sizeof($this->wfo) == 0){ return "1 = 1"; }

    $sql = "w.wfo IN ('". implode(",", $this->wfo) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function sqlLSRTypeBuilder(){
    reset($this->ltype);
    if (sizeof($this->ltype) == 0){ return "1 = 1"; }
    $l = Array();
    while( list($k,$v) = each($this->ltype)){
        if ($v == "TO"){ $l[] = "T"; }
        else if ($v == "SV"){ $l[] = "H"; $l[] = "G"; $l[] = "D"; }
        else if ($v == "MA"){ $l[] = "M"; $l[] = "W"; }
        else if ($v == "FF"){ $l[] = "F"; };
    }   
    $sql = "type IN ('". implode(",", $l) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function sqlTypeBuilder(){
    if (sizeof($this->wtype) == 0) return "1 = 1";

    $sql = "phenomena IN ('". implode(",", $this->wtype) ."')";
    $sql = str_replace(",", "','", $sql);
    return $sql;
}

function computeAverageSize(){
    if (sizeof($this->warnings) == 0){ return 0; }
    reset($this->warnings);
    $polysz = 0;
    while (list($k,$v) = each($this->warnings)){
        $polysz += $v["parea"];
    }
    return $polysz / floatval(sizeof($this->warnings));
}

function computeSizeReduction(){
    reset($this->warnings);
    $polysz = 0;
    $countysz = 0;
    while (list($k,$v) = each($this->warnings)){
        $polysz += $v["parea"];
        while (list($k2,$v2) = each($v["ugc"])){
            $countysz += $this->ugcCache[$v2]["area"];
        }
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
    while (list($k,$v) = each($this->lsrs)){
        if ($v["warned"]){ $counter += 1; }
    }
    return $counter;
}

function computeTDQEvents(){
    if (sizeof($this->lsrs) == 0){ return 0; }

    reset($this->lsrs);
    $counter = 0;
    while (list($k,$v) = each($this->lsrs)){
        if ($v["tdq"]){ $counter += 1; }
    }
    return $counter;
}

function computeMaxLeadTime(){
   if (sizeof($this->lsrs) == 0){ return 0; }

   $large = 0;
   reset($this->lsrs);
   while (list($k,$v) = each($this->lsrs)){
       if ($v["leadtime"] > $large){ $large = $v["leadtime"]; }
   }
   return $large;
}
function computeMinLeadTime(){
   if (sizeof($this->lsrs) == 0){ return 0; }
   $smallest = 99;
   reset($this->lsrs);
   while (list($k,$v) = each($this->lsrs)){
       if ($v["leadtime"] < $smallest){ $smallest = $v["leadtime"]; }
   }
   return $smallest;
}


function computeAllLeadTime(){
   $ar = Array();
   reset($this->lsrs);
   while (list($k,$v) = each($this->lsrs)){
       if ($v["leadtime"] != "NA"){ $ar[] = $v["leadtime"]; }
   }
   if (sizeof($ar) == 0){ return 0; }
   return array_sum($ar) / floatval( sizeof($ar) );
}

function computeAverageLeadTime(){
   $ar = Array();
   reset($this->warnings);
   while (list($k,$v) = each($this->warnings)){
       if ($v["lead0"] > -1){ $ar[] = $v["lead0"]; }
   }
   if (sizeof($ar) == 0){ return 0; }
   return array_sum($ar) / floatval( sizeof($ar) );
}

function computeAveragePerimeterRatio(){
   $shared = 0;
   $total = 0;
   reset($this->warnings);
   while (list($k,$v) = each($this->warnings)){
       $shared += $v["sharedborder"];
       $total += $v["perimeter"];
   }
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
    while (list($k,$v) = each($this->warnings)){
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
    while (list($k,$v) = each($this->warnings)){
        if ($v["verify"]){ $counter += 1; }
    }
    return $counter;
}

function computeWarningsUnverified(){
    return sizeof($this->warnings) - $this->computeWarningsVerified();
}

function computeUGC(){
    reset($this->warnings);
    while (list($k,$v) = each($this->warnings)){
        while (list($k2,$v2) = each($v["ugc"])){
            if (array_key_exists($v2, $this->ugcCache)){ continue; }
            /* Else we need to lookup the informations */
            $sql = sprintf("SELECT *, 
                   area(transform(geom,2163)) / 1000000.0 as area 
                   from nws_ugc WHERE ugc = '%s'", $v2);
            $rs = $this->callDB($sql);
            if (pg_num_rows($rs) > 0){
                $row = pg_fetch_array($rs,0);
                $this->ugcCache[$v2] = Array(
                     "name" => sprintf("%s,%s ", $row["name"], $row["state"]),
                     "area" => $row["area"]);
            } else {
                $this->ugcCache[$v2] = Array(
                     "name" => sprintf("(((%s)))", $v2),
                     "area" => $row["area"]);
            }
        }
    }
} /* End of computeUGC() */

function computeSharedBorder(){
    reset($this->warnings);
    while (list($k,$v) = each($this->warnings)){
        $sql = sprintf("SELECT sum(sz) as s from (
     SELECT length(transform(a,2163)) as sz from (
        select 
           intersection(
      buffer(exteriorring(geometryn(multi(geomunion(n.geom)),1)),0.02),
      exteriorring(geometryn(multi(geomunion(w.geom)),1))
            )  as a
            from warnings_%s w, nws_ugc n WHERE gtype = 'P' 
            and w.wfo = '%s' and phenomena = '%s' and eventid = '%s' 
            and significance = '%s' and n.polygon_class = 'C'
            and st_overlaps(n.geom, w.geom) 
            and n.ugc IN (
                SELECT ugc from warnings_%s w WHERE
                gtype = 'C' and wfo = '%s'
          and phenomena = '%s' and eventid = '%s' and significance = '%s'
       )
         ) as foo
            WHERE not isempty(a) ) as foo
       ", date("Y", $this->sts), $v["wfo"], $v["phenomena"],
            $v["eventid"], $v["significance"],
          date("Y", $this->sts), $v["wfo"], $v["phenomena"],
            $v["eventid"], $v["significance"] );

        $rs = $this->callDB($sql);
        if ($rs && pg_num_rows($rs) > 0){
            $row = pg_fetch_array($rs,0);
            $this->warnings[$k]["sharedborder"] = $row["s"];
        } else {
            $this->warnings[$k]["sharedborder"] = 0;
        }
    }
}

function loadWarnings(){
    $sql = sprintf("
    select *, astext(geom) as tgeom from 
      (SELECT distinct * from 
        (select *, area(transform(geom,2163)) / 1000000.0 as area,
         perimeter(transform(geom,2163)) as perimeter,
         xmax(geom) as lon0, ymax(geom) as lat0 from 
         warnings_%s w WHERE %s and issue >= '%s' and issue < '%s' and
         expire < '%s' and %s and significance = 'W' 
         ORDER by issue ASC) as foo) 
      as foo2", date("Y", $this->sts), $this->sqlWFOBuilder(), 
   date("Y/m/d H:i", $this->sts), date("Y/m/d H:i", $this->ets), 
   date("Y/m/d H:i", $this->ets), $this->sqlTypeBuilder() );

    $rs = $this->callDB($sql);
    for ($i=0;$row = @pg_fetch_array($rs,$i);$i++){
        $key = sprintf("%s-%s-%s-%s", date("Y", $this->sts), $row["wfo"], 
                       $row["phenomena"], $row["eventid"]);
        if ( ! isset($this->warnings[$key]) ){
            $this->warnings[$key] = Array("ugc"=> Array(), "geom" => "",
                                          "lsrs" => Array() );
        }
        $this->warnings[$key]["issue"] = $row["issue"];
        $this->warnings[$key]["expire"] = $row["expire"];
        $this->warnings[$key]["phenomena"] = $row["phenomena"];
        $this->warnings[$key]["wfo"] = $row["wfo"];
        $this->warnings[$key]["status"] = $row["status"];
        $this->warnings[$key]["significance"] = $row["significance"];
        $this->warnings[$key]["area"] = $row["area"];
        $this->warnings[$key]["lat0"] = $row["lat0"];
        $this->warnings[$key]["lon0"] = $row["lon0"];
        $this->warnings[$key]["sts"] = strtotime($row["issue"]);
        $this->warnings[$key]["ets"] = strtotime($row["expire"]);
        $this->warnings[$key]["eventid"] = $row["eventid"];
        $this->warnings[$key]["lead0"] = -1;
        $this->warnings[$key]["buffered"] = 0;
        $this->warnings[$key]["verify"] = 0;
        if ($row["gtype"] == "P"){
            $this->warnings[$key]["geom"] = $row["tgeom"];
            $this->warnings[$key]["perimeter"] = $row["perimeter"];
            $this->warnings[$key]["parea"] = $row["area"];
        } else {
            $this->warnings[$key]["ugc"][] = $row["ugc"];
        }

    } /* End of rs for loop */

} /* End of loadWarnings() */

function loadLSRs() {
    $sql = sprintf("SELECT distinct *, x(geom) as lon0, y(geom) as lat0, 
        astext(geom) as tgeom,
        astext(buffer( transform(geom,2163), %s000)) as buffered
        from lsrs_%s w WHERE %s and 
        valid >= '%s' and valid < '%s' and %s and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= %s) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
        ORDER by valid ASC", $this->lsrbuffer, 
        date("Y", $this->sts), $this->sqlWFOBuilder(), 
        date("Y/m/d H:i", $this->sts), date("Y/m/d H:i", $this->ets), 
        $this->sqlLSRTypeBuilder(), $this->hailsize);
    $rs = $this->callDB($sql);
    for ($i=0;$row = @pg_fetch_array($rs,$i);$i++)
    {
        $key = sprintf("%s-%s-%s-%s-%s", 
          $row["wfo"], $row["valid"], $row["type"],
          $row["magnitude"], $row["city"]);
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
    reset($this->warnings);
    while (list($k,$v) = each($this->warnings)) {
        if (sizeof($v["lsrs"]) == 0){ continue; }
        $bufferedArray = Array();
        while (list($k2,$v2) = each($v["lsrs"])){
            $bufferedArray[] = sprintf("SetSRID(GeomFromText('%s'),2163)", 
              $this->lsrs[$v2]["buffered"]);
        }
        $sql = sprintf("SELECT ST_Area(
         ST_Intersection( ST_Union(ARRAY[%s]), 
                          ST_Transform(ST_GeomFromEWKT('SRID=4326;%s'),2163) ) 
         ) / 1000000.0 as area",
         implode(",", $bufferedArray), $v["geom"] );
        $rs = $this->callDB($sql);
        if ($rs){
            $row = pg_fetch_array($rs,0);
        } else {
            $row = Array("area" => 0);
        }
        $this->warnings[$k]["buffered"] = $row["area"];
    }
}

function sbwVerify() {
    reset($this->warnings);
    while (list($k,$v) = each($this->warnings)) {
        /* Look for LSRs! */
        $sql = sprintf("SELECT distinct *
         from lsrs_%s w WHERE 
         geom && SetSrid(GeometryFromText('%s'),4326) and 
         contains(SetSrid(GeometryFromText('%s'),4326), geom) 
         and %s and wfo = '%s' and
        ((type = 'M' and magnitude >= 34) or 
         (type = 'H' and magnitude >= %s) or type = 'W' or
         type = 'T' or (type = 'G' and magnitude >= 58) or type = 'D'
         or type = 'F')
         and valid >= '%s' and valid <= '%s' 
         ORDER by valid ASC", date("Y", $this->sts),
         $v["geom"], $v["geom"], $this->sqlLSRTypeBuilder(), 
         $v["wfo"], $this->hailsize,
         date("Y/m/d H:i", strtotime($v["issue"])),
         date("Y/m/d H:i", strtotime($v["expire"])) );
        $rs = $this->callDB($sql);
        for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
            $key = sprintf("%s-%s-%s-%s-%s", 
                   $row["wfo"], $row["valid"], $row["type"],
                   $row["magnitude"], $row["city"]);
            $verify = False;
            if ($v["phenomena"] == "FF"){
                if ($row["type"] == "F") { $verify = True; }
            }
            else if ($v["phenomena"] == "TO"){
                if ($row["type"] == "T") { $verify = True; }
                else { $this->lsrs[$key]["tdq"] = True; }
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
            if ($verify || $this->lsrs[$key]["tdq"]){ 
                $this->warnings[$k]["lsrs"][] = $key;
                $this->lsrs[$key]["warned"] = True;
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
