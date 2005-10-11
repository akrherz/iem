<?php
//$iem40 = '10.10.10.40';
//$iem20 = '10.10.10.20';
//$iem30 = '10.10.10.30';
$iem40 = 'mesonet.agron.iastate.edu';
$iem20 = 'db1.mesonet.agron.iastate.edu';
$iem30 = 'kcci.mesonet.agron.iastate.edu';
$_DATABASES = Array(
 'access' => "dbname=iem port=9999 host=$iem30 user=nobody",
 'coop' => "dbname=coop host=$iem20 user=nobody",
 'awos' => "dbname=awos host=$iem20 user=nobody",
 'rwis' => "dbname=rwis host=$iem20 user=nobody",
 'wepp' => "dbname=wepp host=$iem20 user=akrherz",
 'snet' => "dbname=snet host=$iem20 user=akrherz",
 'mesosite' => "dbname=mesosite host=$iem40 user=nobody",
 'isuag' => "dbname=isuag host=$iem40 user=akrherz",
 'other' => "dbname=other host=$iem40 user=akrherz",
 'postgis' => "dbname=postgis host=$iem40 user=akrherz",
 'portfolio' => "dbname=portfolio host=meteor.geol.iastate.edu user=mesonet",
);

function iemdb($DBKEY)
{
  global $_DATABASES;
  return pg_connect( $_DATABASES[$DBKEY] );
}
?>
