<?php
 // dbloc.php
 //   Get a location from DB (better than allLoc?)
 //   Daryl Herzmann 6 Dec 2002

function dbloc($c, $sid){
  $sid = substr($sid, 0, 6);
  $q = "SELECT *, x(geom) as longitude, y(geom) as latitude from stations WHERE id = '".$sid."'";
  $rs = pg_exec($c, $q);
  pg_close($c);

  $row = @pg_fetch_array($rs,0);
  $row["lon"] = $row["longitude"];
  $row["lat"] = $row["latitude"];
  return $row;

} // End of dbloc()

//select Y(transform(geometryfromtext(ba, 4326), 26915)), X(transform(geometryfromtext(ba, 4326), 26915)) from (select 'POINT('||longitude||' '||latitude||')' as ba from stations WHERE id = 'AMW') as foo;

function dbloc26915($c,$sid){
  $sid = substr($sid, 0, 6);
  $q = "select Y(transform(geometryfromtext(ba, 4326), 26915)), X(transform(geometryfromtext(ba, 4326), 26915)) from (select 'POINT('||x(geom)||' '||y(geom)||')' as ba from stations WHERE id = '$sid') as foo";
  $rs = pg_exec($c, $q);
  pg_close($c);

  $row = @pg_fetch_array($rs,0);
  $r = Array();
  $r["x"] = $row["x"];
  $r["y"] = $row["y"];
  return $r;

} // End of dbloc()


?>
