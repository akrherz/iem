<?php
/**
 * Time for a standard library to access the IEMAccess DB for observations
 *  This could theoretically be distributed to others to access the DB!
 * Daryl Herzmann 18 June 2003
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
    $rs = pg_exec($this->dbconn, sprintf("select *, x(c.geom) as x, y(c.geom) as y, 
    valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from current c LEFT JOIN summary s USING (station, network) WHERE c.station = '$sid' and s.day = 'TODAY'", $this->tzname, $this->tzname,$this->tzname));
    return new IEMAccessOb(@pg_fetch_array($rs,0));
  }

  function getSingleSiteYest($sid) {
    $rs = pg_exec($this->dbconn, sprintf("select *, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from current c LEFT JOIN summary s 
    USING (station, network) WHERE c.station = '$sid' and s.day = 'YESTERDAY'", $this->tzname, $this->tzname,$this->tzname ));
    return new IEMAccessOb(pg_fetch_array($rs,0));
  }

  function getNetwork($network) {
    $ret = Array();
    $sql = sprintf("select *, c.pday as ob_pday, x(c.geom) as x, 
    y(c.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from 
    current c LEFT JOIN summary s USING (station, network) 
    WHERE c.network = '$network' and s.day = date(now() at time zone '%s')",
    $this->tzname, $this->tzname, $this->tzname, $this->tzname);
    $rs = pg_exec($this->dbconn, $sql);
    for( $i=0; $row = @pg_fetch_assoc($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }

  function getAll() {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select *, x(c.geom) as x, y(c.geom) as y, valid at time zone '%s' as lvalid,
    max_gust_ts at time zone '%s' as lmax_gust_ts,
    max_sknt_ts at time zone '%s' as lmax_sknt_ts from current c LEFT JOIN summary s USING (station, network) WHERE c.network IN ('IA_RWIS', 'IA_ASOS', 'AWOS', 'KCCI', 'KIMT') and s.day = 'TODAY' and c.valid > 'TODAY' ");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
    }
    return $ret;
  }


  function getNetworkSummary($network, $valid) {
    $ret = Array();
    $rs = pg_exec($this->dbconn, "select *, x(c.geom) as x, y(c.geom) as y from current c LEFT JOIN summary s USING (station, network) WHERE c.network = '$network' and s.day = '$valid'");
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
      $ret[$row["station"]] = new IEMAccessOb($row);
      $ret[$row["station"]]->db["obtime"] = $valid;
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
