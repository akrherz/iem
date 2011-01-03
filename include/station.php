<?php
/* Build Network station tables on demand! */

include_once("$rootpath/include/database.inc.php");

class StationData {

  function StationData($a,$n="")
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");
    if ($n != ""){
    	$rs = pg_prepare($this->dbconn, "SELECT  ST", "SELECT *, " .
    		"x(geom) as lon, y(geom) as lat from stations " .
    		"WHERE id = $1 and network = $2");
    } else{
    	$rs = pg_prepare($this->dbconn, "SELECT  ST", "SELECT *, " .
    		"x(geom) as lon, y(geom) as lat from stations " .
    		"WHERE id = $1");
    }
    if (is_string($a)) $this->load_station($a,$n);
    else if (is_array($a)) 
    {
      foreach($a as $id) { $this->load_station($id,$n); }
    }

  }

  function load_station($id,$n="")
  {
  	if ($n != ""){ 
    	$rs = pg_execute($this->dbconn, "SELECT  ST", Array($id,$n));
  	} else{
  		$rs = pg_execute($this->dbconn, "SELECT  ST", Array($id));
  	}
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
