<?php

function getstations($fips){

  $con = pg_connect("localhost", 5432, "mesosite");
  $sqlStr = select s.id as id , s.name as name from stations s, counties n 
            WHERE n.fips = '$fips' and s.geom && n.the_geom ;
  $result = pg_exec($con, $sqlStr);
  pg_close($con);

  return $result

}

?>
