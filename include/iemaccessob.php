<?php

class IEMAccessOb {

  function IEMAccessOb($row){
    $this->ts = strtotime($row["valid"]);
    $this->db = $row;
    $this->db["ts"] = strtotime(substr($row["valid"],0,16));
    $this->db["gust_ts"] = strtotime(substr($row["max_gust_ts"],0,16));
    $this->db["obtime"] = strftime("%I:%M %p", $this->db["ts"]);
  }
  

}

?>
