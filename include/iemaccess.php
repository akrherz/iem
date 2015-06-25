<?php
/**
 * Time for a standard library to access the IEMAccess DB for observations
 *  This could theoretically be distributed to others to access the DB!
 */

include_once dirname(__FILE__) ."/database.inc.php";

class IEMAccess {
  var $dbconn;

  function IEMAccess($tzname="America/Chicago") {
    $this->dbconn = iemdb("access");
    $this->tzname = $tzname;
 
  } // End of IEMAccess Constructor

  function query($sql) {
    return pg_exec($this->dbconn, $sql);
  }

  function getSingleSite($sid) {
    $sid = strtoupper($sid);
    $rs = pg_exec($this->dbconn, sprintf("select *, 
    ST_x(s.geom) as x, ST_y(s.geom) as y, 
    valid at time zone s.tzname as lvalid,
    valid at time zone 'UTC' as utc_valid,
    max_gust_ts at time zone s.tzname as lmax_gust_ts,
    max_sknt_ts at time zone s.tzname as lmax_sknt_ts,
    s.name as sname from 
    current c2, summary_%s c, stations s WHERE 
    s.id = '$sid' and c.iemid = s.iemid and s.iemid = c2.iemid
    and c.day = date(now() at time zone s.tzname)",  date("Y")));
    return new IEMAccessOb(@pg_fetch_array($rs,0));
  }

  function getNetwork($network) {
  	if (is_array($network)){
		$nstring = "s.network in (";
  		while (list($key,$value) = each($network)){
  			$nstring .= "'$value',";
  		}
		$nstring .= "'X')";
  	}
  	else {
  		$nstring = sprintf("s.network = '%s'", $network);
  	}
    $ret = Array();
    $sql = sprintf("select s.id, s.id as station, *, c.pday as ob_pday, 
    		ST_x(s.geom) as x, ST_y(s.geom) as y, 
    		valid at time zone s.tzname as lvalid,
    		valid at time zone 'UTC' as utc_valid,
    max_gust_ts at time zone s.tzname as lmax_gust_ts,
    max_sknt_ts at time zone s.tzname as lmax_sknt_ts,
    s.name as sname from 
    current c2, summary_%s c, stations s  
    WHERE $nstring and c.iemid = s.iemid and c2.iemid = c.iemid and
    c.day = date(now() at time zone '%s') ORDER by random() ASC",
     date("Y"), 
    $this->tzname);
    $rs = pg_exec($this->dbconn, $sql);
    for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
      $ret[$row["id"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function getIowa() {
    $ret = Array();
    $rs = pg_exec($this->dbconn, sprintf("select *, 
    ST_x(s.geom) as x, ST_y(s.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts,
    		valid at time zone 'UTC' as utc_valid,
    s.name as sname from 
    current c2, summary_%s c, stations s WHERE 
    s.network IN ('IA_RWIS', 'IA_ASOS', 'AWOS', 'KCCI', 'KIMT') 
    and c.day = 'TODAY' 
    and c2.valid > 'TODAY' and c2.iemid = c.iemid and c.iemid = s.iemid", 
    $this->tzname, $this->tzname, $this->tzname, date("Y")));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["id"]] = new IEMAccessOb($row);
    }
    return $ret;
  }
  function getState($state) {
  	$ret = Array();
  	$rs = pg_prepare($this->dbconn, "STATESELECT", sprintf("select *,
    ST_x(s.geom) as x, ST_y(s.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts,
  			valid at time zone 'UTC' as utc_valid,
    s.name as sname from
    current c2, summary_%s c, stations s WHERE
    s.state = $1 and (s.network ~* 'RWIS' or s.network ~* 'ASOS' or
  			s.network in ('KCCI','KELO','KIMT') or network = 'AWOS') 
    and c.day = 'TODAY'
    and c2.valid > 'TODAY' and c2.iemid = c.iemid and c.iemid = s.iemid",
  			$this->tzname, $this->tzname, $this->tzname, date("Y")));
  	$rs = pg_execute($this->dbconn, "STATESELECT", Array($state));
  	for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  		$ret[$row["id"]] = new IEMAccessOb($row);
  	}
  	return $ret;
  }
  function getWFO($wfo) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, sprintf("select *, 
    ST_x(s.geom) as x, ST_y(s.geom) as y, valid at time zone s.tzname as lvalid,
    max_gust_ts at time zone s.tzname as lmax_gust_ts,
    max_sknt_ts at time zone s.tzname as lmax_sknt_ts,
    		valid at time zone 'UTC' as utc_valid,
    s.name as sname from 
    current c2, summary_%s c, stations s WHERE 
    s.wfo = '%s' 
    and c.day = date(now() at time zone s.tzname) 
    and c2.valid > date(now() at time zone s.tzname)
    and c2.iemid = c.iemid and c.iemid = s.iemid", 
    date("Y"), $wfo));
    for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
      $ret[$row["id"]] = new IEMAccessOb($row);
    }
    return $ret;
  }
  function getWFO_COOP($wfo) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, sprintf("select *, 
    ST_x(s.geom) as x, ST_y(s.geom) as y, valid at time zone s.tzname as lvalid,
    max_gust_ts at time zone s.tzname as lmax_gust_ts,
    max_sknt_ts at time zone s.tzname as lmax_sknt_ts,
    		valid at time zone 'UTC' as utc_valid,
    s.name as sname from 
    current c2, summary_%s c, stations s WHERE 
    s.wfo = '%s' 
    and c.day = date(now() at time zone s.tzname) 
	and s.network ~* 'COOP'
    and c2.iemid = c.iemid and c.iemid = s.iemid", 
    date("Y"), $wfo));
    for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
      $ret[$row["id"]] = new IEMAccessOb($row);
    }
    return $ret;
  }
  
  function ge_max_tmpf($size) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select *,
    		valid at time zone 'UTC' as utc_valid from current WHERE
      valid > (CURRENT_TIMESTAMP - '70 minutes'::interval) and tmpf < 140
      ORDER by tmpf DESC LIMIT $size");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function ge_min_tmpf($size) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select *,
    		valid at time zone 'UTC' as utc_valid from current WHERE
      valid > (CURRENT_TIMESTAMP - '70 minutes'::interval) and tmpf > -50
      ORDER by tmpf ASC LIMIT $size");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

}
?>
