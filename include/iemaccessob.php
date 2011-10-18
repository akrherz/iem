<?php

class IEMAccessOb {

  function IEMAccessOb($row){
  	$this->db = Array();
    if ($row == ""){ $this->invalid = 1; return; }
    $this->ts = strtotime($row["valid"]);
    $this->lts = strtotime($row["lvalid"]);
    $this->db = $row;
    $this->db["ts"] = strtotime(substr($row["valid"],0,16));
    if ($row["max_gust_ts"] != ""){
      $this->db["gust_ts"] = strtotime(substr($row["max_gust_ts"],0,16));
      $this->db["lgust_ts"] = strtotime(substr($row["lmax_gust_ts"],0,16));
    }
    $this->db["obtime"] = strftime("%I:%M %p", $this->db["ts"]);
    if ($this->db["max_tmpf"] == -99){
    	$this->db["max_tmpf"] = null;
    }
  	if ($this->db["min_tmpf"] == 99){
    	$this->db["min_tmpf"] = null;
    }
  }
  

}

?>
