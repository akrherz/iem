<?php
// Library to handle php access to current data...
//  Call with something like $stData = currentSFOb("AMW");


//___________________________________________________________
function currentSFOb_rwis($station){
  include('rwisLoc.php');
  $dataDir = '/mesonet/data/current/rwis_sf/';
  $fc = implode('', file($dataDir . $station .".dat") );
  $rwisFormat = Array("station", "gmt_ts", "tmpf0", "dry0", 
     "tmpf1", "dry1", "tmpf2", "dry2", "tmpf3", "dry3", "subt");
  $stData = cdf2($fc, $rwisFormat);
  $stData["gmt_ts"] = mktime(substr($stData["gmt_ts"],11,13),
   substr($stData["gmt_ts"],14,16), substr($stData["gmt_ts"],17,19),
   substr($stData["gmt_ts"],5,7), substr($stData["gmt_ts"],8,10),
   substr($stData["gmt_ts"],0,4));
  $stData["city"] = $Rcities[$station]["city"];

  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  $stData["network"] = "RWIS";
  return $stData;
} // End of currentOb_rwis

//____________________________________________________________
function cdf2($fc, $format){
  $tokens = split(",", $fc);
  $stData = Array();
  while( list($key, $val) = each($format) ){
#    echo $tokens[$key] ." == ". $format[$key] ;
    $stData[$format[$key]] = $tokens[$key];
  } // End of while
  return $stData;
} // End of cdf

//___________________________________________________________
function currentSFOb($station){

  $stLength = strlen($station);
  switch ($stLength){
    case 4: // RWIS!
      $stData = currentSFOb_rwis($station);
      break;
  }
  return $stData;
} // End of currentOb

//______________________________________________________________
// \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
//                 Generic Helper Functions
// /////////////////////////////////////////////////////////////
//--------------------------------------------------------------

?>
