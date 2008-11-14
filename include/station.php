<?php
/* Build Network station tables on demand! */

include_once("$rootpath/include/database.inc.php");

class StationData {

  function StationData($a)
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");
    $rs = pg_prepare($this->dbconn, "SELECTST", "SELECT *, x(geom) as lon, y(geom) as lat from stations WHERE id = $1");
    if (is_string($a)) $this->load_station($a);
    else if (is_array($a)) 
    {
      foreach($a as $id) { $this->load_station($id); }
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
