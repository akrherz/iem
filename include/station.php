<?php
/* Build Network station tables on demand! */

include_once("$rootpath/include/database.inc.php");

class StationData {

  function StationData($a)
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");
    if (is_string($a)) $this->load_station($a);
    else if (is_array($a)) 
    {
      foreach($a as $network) { $this->load_station($a); }
    }

  }

  function load_station($id)
  {
    $rs = pg_prepare($this->dbconn, "SELECT", "SELECT *, x(geom) as lon, y(geom) as lat from stations WHERE id = $1");
    $rs = pg_execute($this->dbconn, "SELECT", Array($id));
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
