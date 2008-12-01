<?php
/* Build Network station tables on demand! */

include_once("$rootpath/include/database.inc.php");

class NetworkTable {

  function NetworkTable($a)
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");
    $rs = pg_prepare($this->dbconn, "SELECT", "SELECT *, x(geom) as lon, y(geom) as lat from stations WHERE network = $1 ORDER by name ASC");
    $rs = pg_prepare($this->dbconn, "SELECTST", "SELECT *, x(geom) as lon, y(geom) as lat from stations WHERE id = $1");
    if (is_string($a)) $this->load_network($a);
    else if (is_array($a)) 
    {
      foreach($a as $network) { $this->load_network($network); }
    }

  }

  function load_network($network)
  {
    $rs = pg_execute($this->dbconn, "SELECT", Array($network));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
    {
      $this->table[ $row["id"] ] = $row;
    }
  }

  function load_station($id)
  {
    $rs = pg_execute($this->dbconn, "SELECTST", Array($id));
    for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
    {
      $this->table[ $row["id"] ] = $row;
    }
  }


  function get($id)
  {
    return $this->table[$id];
  }
}

?>
