<?php
/* Build Network station tables on demand! */

include_once dirname(__FILE__) ."/network.php";

class StationData {

  function __construct($a,$n="")
  {
    $this->table = Array();
    $this->dbconn = iemdb("mesosite");

    $rs = pg_prepare($this->dbconn, "SELECT  ST1", "SELECT *, " .
    		"ST_x(geom) as lon, ST_y(geom) as lat from stations " .
    		"WHERE id = $1 and network = $2");
    $rs = pg_prepare($this->dbconn, "SELECT  ST2", "SELECT *, " .
    		"ST_x(geom) as lon, ST_y(geom) as lat from stations " .
    		"WHERE id = $1");
    
    if (is_string($a)) $this->load_station($a,$n);
    else if (is_array($a)) 
    {
      foreach($a as $id) { $this->load_station($id,$n); }
    }

  }

  function load_station($id,$n="")
  {
  	if ($n != ""){ 
    	$rs = pg_execute($this->dbconn, "SELECT  ST1", Array($id,$n));
  	} else{
  		$rs = pg_execute($this->dbconn, "SELECT  ST2", Array($id));
  	}
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
  }
  
  function get($id)
  {
    return $this->table[$id];
  }
}

?>
