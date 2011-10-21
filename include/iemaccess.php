<?php
/**
 * Time for a standard library to access the IEMAccess DB for observations
 *  This could theoretically be distributed to others to access the DB!
 * $Id: $:
 */

include_once("$rootpath/include/database.inc.php");

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
    x(s.geom) as x, y(s.geom) as y, 
    valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from 
    current c2, summary_%s c, stations s WHERE 
    c.station = '$sid' and c.station = s.id and c.network = s.network
    and c2.station = s.id and c2.network = s.network 
    and c.day = date(now() at time zone s.tzname)", 
    $this->tzname, $this->tzname,$this->tzname, date("Y")));
    return new IEMAccessOb(@pg_fetch_array($rs,0));
  }

  function getNetwork($network) {
    $ret = Array();
    $sql = sprintf("select *, c.pday as ob_pday, x(s.geom) as x, 
    y(s.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from 
    current c2, summary_%s c, stations s  
    WHERE c.network = '$network' and c.network = c2.network and
    c.network = s.network and c.station = s.id and 
    s.id = c2.station and 
    c.day = date(now() at time zone '%s')",
    $this->tzname, $this->tzname, $this->tzname, date("Y"), 
    $this->tzname);
    $rs = pg_exec($this->dbconn, $sql);
    for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function getIowa() {
    $ret = Array();
    $rs = pg_exec($this->dbconn, sprintf("select *, 
    x(s.geom) as x, y(s.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from 
    current c2, summary_%s c, stations s WHERE 
    c.network IN ('IA_RWIS', 'IA_ASOS', 'AWOS', 'KCCI', 'KIMT') 
    and c.day = 'TODAY' 
    and c2.valid > 'TODAY' and s.network = c.network and
    c.network = c2.network and s.id = c.station and 
    c.station = c2.station", $this->tzname, 
    $this->tzname, $this->tzname, date("Y")));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function ge_max_tmpf($size) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select * from current WHERE
      valid > (CURRENT_TIMESTAMP - '70 minutes'::interval) and tmpf < 140
      ORDER by tmpf DESC LIMIT $size");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function ge_min_tmpf($size) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select * from current WHERE
      valid > (CURRENT_TIMESTAMP - '70 minutes'::interval) and tmpf > -50
      ORDER by tmpf ASC LIMIT $size");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

}
?>
