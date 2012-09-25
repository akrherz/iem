<?php
/*
 * Database connection function that most every script uses :)
 * $Id: $:
 */
$iem20 = 'iemdb';
global $_DATABASES;
$_DATABASES = Array(
 'access' => "dbname=iem host=$iem20 user=nobody connect_timeout=5",
 'iem' => "dbname=iem host=$iem20 user=nobody connect_timeout=5",
 'afos' => "dbname=afos host=$iem20 user=nobody connect_timeout=5",
 'hads' => "dbname=hads host=$iem20 user=nobody connect_timeout=5",
 'asos' => "dbname=asos host=$iem20 user=nobody connect_timeout=5",
 'coop' => "dbname=coop host=$iem20 user=nobody connect_timeout=5",
 'awos' => "dbname=awos host=$iem20 user=nobody connect_timeout=5",
 'mos' => "dbname=mos host=$iem20 user=nobody connect_timeout=5",
 'rwis' => "dbname=rwis host=$iem20 user=nobody connect_timeout=5",
 'wepp' => "dbname=wepp host=$iem20 user=nobody connect_timeout=5",
 'snet' => "dbname=snet host=$iem20 user=nobody connect_timeout=5",
 'mesosite' => "dbname=mesosite host=$iem20 user=nobody connect_timeout=5",
 'isuag' => "dbname=isuag host=$iem20 user=nobody connect_timeout=5",
 'other' => "dbname=other host=$iem20 user=nobody connect_timeout=5",
 'postgis' => "dbname=postgis host=$iem20 user=nobody connect_timeout=5",
 'portfolio' => "dbname=portfolio host=meteor.geol.iastate.edu user=mesonet connect_timeout=5",
 'scan' => "dbname=scan host=$iem20 user=nobody connect_timeout=5",
 'squaw' => "dbname=squaw host=$iem20 user=nobody connect_timeout=5",
);

function database_failure($DBKEY)
{
	echo sprintf("<div class='warning'>Unable to contact database: %s</div>", $DBKEY);
}

function iemdb($DBKEY, $force_new=0)
{
  global $_DATABASES;
  $db = pg_connect( $_DATABASES[$DBKEY] , $force_new) or database_failure($DBKEY);
  return $db;
}
?>
