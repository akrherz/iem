  $connection = pg_connect("localhost", 5432, "mesosite");
  $rs = pg_exec($connection, "SELECT *  from stations WHERE id = '". $id ."' ");
  pg_close($connection);

  $row = @pg_fetch_array($rs,0);

