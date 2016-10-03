<?php
/*
 * Database connection function that most every script uses :)
 */

// TODO replace this with a generating function, update PHP scripts that
// reference this $_DATABASES array :(
global $_DATABASES;
$_DATABASES = Array(
 'access' => "dbname=iem host=iemdb user=nobody connect_timeout=5",
 'iem' => "dbname=iem host=iemdb user=nobody connect_timeout=5",
 'afos' => "dbname=afos host=iemdb user=nobody connect_timeout=5",
 'hads' => "dbname=hads host=iemdb-hads user=nobody connect_timeout=5",
 'asos' => "dbname=asos host=iemdb user=nobody connect_timeout=5",
 'coop' => "dbname=coop host=iemdb user=nobody connect_timeout=5",
 'awos' => "dbname=awos host=iemdb user=nobody connect_timeout=5",
 'mos' => "dbname=mos host=iemdb user=nobody connect_timeout=5",
 'rwis' => "dbname=rwis host=iemdb user=nobody connect_timeout=5",
 'wepp' => "dbname=wepp host=iemdb user=nobody connect_timeout=5",
 'snet' => "dbname=snet host=iemdb user=nobody connect_timeout=5",
 'mesosite' => "dbname=mesosite host=iemdb user=nobody connect_timeout=5",
 'isuag' => "dbname=isuag host=iemdb user=nobody connect_timeout=5",
 'other' => "dbname=other host=iemdb user=nobody connect_timeout=5",
 'postgis' => "dbname=postgis host=iemdb user=nobody connect_timeout=5",
 'portfolio' => "dbname=portfolio host=iemdb user=nobody connect_timeout=5",
 'scan' => "dbname=scan host=iemdb user=nobody connect_timeout=5",
 'squaw' => "dbname=squaw host=iemdb user=nobody connect_timeout=5",
);

function database_failure($DBKEY)
{
	echo sprintf("<div class='warning'>Unable to contact database: %s</div>", $DBKEY);
}

/*
 * Help function that yields database connections
 */
function iemdb($dbname, $force_new=0, $rw=FALSE)
{
	$dbuser = "nobody";
	$dbhost = "iemdb"; // read-only host
	if ($rw) $dbhost = "iemdb"; // rw master
	if ($dbname == "access"){ $dbname = "iem"; }
	if ($dbname == "hads") $dbhost = "iemdb-hads";
	
	$connstr = sprintf("dbname=%s host=%s user=%s connect_timeout=5",
			$dbname, $dbhost, $dbuser);
	$db = pg_connect( $connstr , $force_new);
	if (! $db ){
		$connstr = sprintf("dbname=%s host=%s user=%s connect_timeout=5",
				$dbname, "iemdb2", $dbuser);
		$db = pg_connect( $connstr, $force_new);
	}
	if (! $db){
		database_failure($dbname);
	}
  	return $db;
} // End of iemdb()
?>
