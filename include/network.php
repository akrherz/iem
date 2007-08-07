<?php
/* Build Network station tables on demand! */

include_once("$rootpath/include/database.inc.php");

class NetworkTable {

  function NetworkTable($a)
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");
    if (is_string($a)) $this->load_network($a);
    else if (is_array($a)) 
    {
      foreach($a as $network) { $this->load_network($a); }
    }

  }

  function load_network($network)
  {
    $rs = pg_exec($this->dbconn, "SELECT * from stations WHERE network = '$network'");
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
