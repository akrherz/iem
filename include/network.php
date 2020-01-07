<?php
// Build Network station tables on demand!

require_once dirname(__FILE__) ."/database.inc.php";

class NetworkTable {

  function __construct($a, $force3char=FALSE)
  {
    $this->table = Array();
    // We force new here to prevent reused prepared statement names, hack
    $this->dbconn = iemdb("mesosite", PGSQL_CONNECT_FORCE_NEW);
    $rs = pg_prepare($this->dbconn, "SELECT", "SELECT *, ST_x(geom) as lon, 
    	ST_y(geom) as lat from stations WHERE network = $1 ORDER by name ASC");
    $rs = pg_prepare($this->dbconn, "SELECTST", "SELECT *, ST_x(geom) as lon, 
    	ST_y(geom) as lat from stations WHERE id = $1");
    if (is_string($a)) $this->load_network($a, $force3char);
    else if (is_array($a)) 
    {
      foreach($a as $network) { $this->load_network($network, $force3char); }
    }
  }

  function load_network($network, $force3char=FALSE)
  {
    $rs = pg_execute($this->dbconn, "SELECT", Array($network));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
    {
        $keyid = $row["id"];
        if ($force3char && strlen($keyid) == 4){
            $keyid = substr($keyid, 1, 3);
        }
        $this->table[$keyid] = $row;
        $this->do_conversions($keyid);
    }
  }

  function load_station($id)
  {
    $rs = pg_execute($this->dbconn, "SELECTST", Array($id));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
    {
      $this->table[ $row["id"] ] = $row;
      $this->do_conversions($row["id"]);
    }
    if (pg_num_rows($rs) < 1){
    	return false;
    }
    return true;
  }

  function do_conversions($id){
      if ($this->table[$id]["archive_begin"] != null){
          $this->table[$id]["archive_begin"] = strtotime($this->table[$id]["archive_begin"]);
      }
      if ($this->table[$id]["archive_end"] != null){
        $this->table[$id]["archive_end"] = strtotime($this->table[$id]["archive_end"]);
    }
}

  function get($id)
  {
    return $this->table[$id];
  }
}

?>