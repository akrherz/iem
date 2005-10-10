<?php
// Library to handle php access to current data...
//  Call with something like $stData = currentOb("AMW");
// 18 Oct 2002:	Have RWIS calculate relative humidity
//  7 Nov 2002:	Also do the snet_max and snet_min files
// 11 Nov 2002: Call feel's like for all of the mods...
// 25 Nov 2002: Fix the trailing /n that was getting with gtim in snet
// 27 Nov 2002: If the RWIS surface temp is missing, set to -99.99
//  4 Dec 2002:	Fix a case when the tempf is below zero!
// 14 Jan 2003:	Vsby is now in the ASOS data...
// 16 Jan 2003:	Updated for the RWIS data processor, we know have more
//		info to use
// 13 Jun 2003	Now we support the RAWS sites and their data


//___________________________________________________________
function currentOb_p($station){
 $dataDir = "/mesonet/data/current/p/";
 $fc = implode('', file($dataDir . $station .".dat") );
 $rawsFormat = Array("sid", "ts", "tmpf", "dwpf", "drct", "sknt", "gust", "relh", "alti", "pcpnCnt", "pDay", "pMonth");
 $stData = cdf($fc, $rawsFormat);
 return $stData;

}


//___________________________________________________________
function currentOb_raws($station){
 $dataDir = "/mesonet/data/current/raws/";
 $fc = implode('', file($dataDir . $station .".dat") );
 $rawsFormat = Array("sid", "gmt_ts", "tmpf", "dwpf", "drct", "sknt", "relh", "pcpn", "srad", "drct_max", "sknt_max");
 $stData = cdf($fc, $rawsFormat);
 $stData["ts"] = $stData["gmt_ts"] - 5*3600;
 return $stData;
}

//___________________________________________________________
function currentOb_snet2($station){
  $dataDir = '/mesonet/data/current/snet_max/';
  $fc = implode('', file($dataDir . $station .".dat") );
//J,082,Max,11/07/02,S,26MPH,049K,460F,068F,098%,30.14",00.00"D,00.11"M,00.00"R,
  $snetFormat = Array("junk", "junk", "junk", "junk", "drctTxt_max",
   "sped_max", "srad_max", "junk", "tmpf_max", "relh_max", "alti_max", 
   "pday_max", "pmonth_max", "prate_max");
  $stData = cdf($fc, $snetFormat);

  $dataDir = '/mesonet/data/current/snet_min/';
  $fc = implode('', file($dataDir . $station .".dat") );
//M,082,Min,11/07/02,NNE,00MPH,000K,460F,032F,030%,29.83",00.00"D,00.11"M,00.00"R,
  $snetFormat = Array("junk", "junk", "junk", "junk", "drctTxt_min",
   "sped_min", "srad_min", "junk", "tmpf_min", "relh_min", "alti_min", 
   "pday_min", "pmonth_min", "prate_max");
  $stData += cdf($fc, $snetFormat);

    $dirTrans = array(
 'N' => '360', 'NNE' => '25', 'NE' => '45', 'ENE' => '70',
 'E' => '90', 'ESE' => '115', 'SE' => '135', 'SSE' => '155',
 'S' => '180', 'SSW' => '205', 'SW' => '225', 'WSW' => '250',
 'W' => '270', 'WNW' => '295', 'NW' => '305', 'NNW' => '335');

  $stData["sped_max"] = intval( substr($stData["sped_max"], 0, 2) );
  $stData["sknt_max"] = round($stData["sped_max"] * 0.868976,0);
  $stData["sped_min"] = intval( substr($stData["sped_min"], 0, 2) );
  $stData["sknt_min"] = round($stData["sped_min"] * 0.868976,0);

  $stData["drct_max"] = $dirTrans[ $stData["drctTxt_max"] ];
  $stData["drct_min"] = $dirTrans[ $stData["drctTxt_min"] ];
  $stData["tmpf_max"] = intval( substr($stData["tmpf_max"], 0, 3) ) ;

  if (substr($stData["tmpf_min"], 0, 2) == "0-"){
    $stData["tmpf_min"] = intval( substr($stData["tmpf_min"], 1, 2) ) ;
  } else {
    $stData["tmpf_min"] = intval( substr($stData["tmpf_min"], 0, 3) ) ;
  }

  $stData["relh_max"] = intval( substr($stData["relh_max"], 0, 3) ) ;
  $stData["relh_min"] = intval( substr($stData["relh_min"], 0, 3) ) ;
  $stData["srad_max"] = intval( substr($stData["srad_max"], 0, 3) ) * 10;
  return $stData;
}
//___________________________________________________________
function currentOb_snet($station){
  include ('snetLoc.php');
  $dataDir = '/mesonet/data/current/ALL/';
  $fc = implode('', file($dataDir . $station .".dat") );
//21:54,07/17/02,S,03MPH,000K,460F,083F,072%,30.01S,00.00"D,02.43"M,00.00"R,14,14,2016
  $snetFormat = Array("time", "date", "drctTxt", "sped",
     "srad", "junk", "tmpf", "relh", "alti", "pday", "pmonth", 
     "prate", "20gu", "gmph", "gtim");
  $stData = cdf($fc, $snetFormat);

  $dirTrans = array(
 'N' => '360', 'NNE' => '25', 'NE' => '45', 'ENE' => '70',
 'E' => '90', 'ESE' => '115', 'SE' => '135', 'SSE' => '155',
 'S' => '180', 'SSW' => '205', 'SW' => '225', 'WSW' => '250',
 'W' => '270', 'WNW' => '295', 'NW' => '305', 'NNW' => '335');

    // Now, we need to fix the schoolnet format to get
  $stData["ts"] = mktime(substr($stData["time"],0,2),
   substr($stData["time"],3,5), 0,
   substr($stData["date"],0,2), substr($stData["date"],3,5),
   substr($stData["date"],6,8));

  $stData["gmt_ts"] = $stData["ts"] + 5*3600;

  $stData["drct"] = $dirTrans[ $stData["drctTxt"] ];
  $stData["sped"] = intval( substr($stData["sped"], 0, 2) );
  $stData["sknt"] = round($stData["sped"] * 0.868976,0);
  $stData["gust"] = round($stData["gmph"] * 0.868976,0);
  $stData["max_sknt"] = $stData["gust"];
  $stData["max_sped"] = $stData["gmph"];
  $stData["srad"] = intval( substr($stData["srad"], 0, 3) ) * 10;

  if (substr($stData["tmpf"], 0, 2) == "0-"){
    $stData["tmpf"] = intval( substr($stData["tmpf"], 1, 2) ) ;
  } else {
    $stData["tmpf"] = intval( substr($stData["tmpf"], 0, 3) ) ;
  }
  $stData["relh"] = intval( substr($stData["relh"], 0, 3) ) ;
  if ($stData["relh"] == 0){
    $stData["dwpf"] = " ";
    $stData["heat"] = " ";
    $stData["relh"] = "0";
  } else {
    $stData["dwpf"] = dwpf($stData["tmpf"], $stData["relh"]);
  }
  $stData["feel"] = feels_like($stData["tmpf"], $stData["relh"], $stData["sped"]);
  $stData["pday"] = substr($stData["pday"], 0, 5);
  $stData["gtim"] = substr($stData["gtim"], 0, 4);
  $stData["pmonth"] = substr($stData["pmonth"], 0, 5);
  $stData["prate"] = substr($stData["prate"], 0, 5);
  $stData["city"] = $Scities[$station]["city"];
  $stData["short"] = $Scities[$station]["short"];
  $stData["network"] = "SNET";
  if (intval($stData["tmpf"]) > 130){
    $stData["tmpf"] = " ";
    $stData["dwpf"] = " ";
    $stData["relh"] = " ";
    $stData["feel"] = " ";
  }
  return $stData;
} // End of currentOb_snet

//___________________________________________________________
function currentSFOb2_rwis($station){
  include('rwisLoc.php');
  $dataDir = '/mesonet/data/current/rwis_sf/';
  $fc = implode('', file($dataDir . $station .".dat") );
  $rwisFormat = Array("station", "gmt_ts", "tmpf0", "dry0",
     "tmpf1", "dry1", "tmpf2", "dry2", "tmpf3", "dry3", "subt");
  $stData = cdf($fc, $rwisFormat);
  $stData["gmt_ts"] = mktime(substr($stData["gmt_ts"],11,13),
   substr($stData["gmt_ts"],14,16), substr($stData["gmt_ts"],17,19),
   substr($stData["gmt_ts"],5,7), substr($stData["gmt_ts"],8,10),
   substr($stData["gmt_ts"],0,4));
  $stData["city"] = $Rcities[$station]["city"];
  if ($stData['tmpf0'] == "") $stData['tmpf0'] = -99.99;
  if ($stData['tmpf1'] == "") $stData['tmpf1'] = -99.99;
  if ($stData['tmpf2'] == "") $stData['tmpf2'] = -99.99;
  if ($stData['tmpf3'] == "") $stData['tmpf3'] = -99.99;
  $t = Array($stData['tmpf0'], $stData['tmpf1'], 
     $stData['tmpf2'], $stData['tmpf3']);
  arsort($t);
  while (min($t) == -99.99){  
    $ba = array_pop($t); 
    if (sizeof($t) == 0) break;
  }
  asort($t);
  if (sizeof($t) > 0){
    while ((max($t) - min($t)) > 20){ $ba = array_pop($t); }
    $stData['pave_avg'] = array_sum($t) / sizeof($t);
  } else {
    $stData['pave_avg'] = -99.99;
  }


  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  $stData["network"] = "RWIS";
  return $stData;
} 


//___________________________________________________________
function currentOb_rwis($station){
  include('rwisLoc.php');
  $dataDir = '/mesonet/data/current/ALL/';
  $fc = implode('', file($dataDir . $station .".dat") );
  $rwisFormat = Array("station", "gmt_ts", "tmpf", "dwpf", 
     "drct", "sknt", "pday", "gust");
  $stData = cdf($fc, $rwisFormat);

  $dataDir = '/mesonet/data/current/asos_ex/';
  $fc = @implode('', @file($dataDir . $station ) );
  $format = Array("bogus", "max_tmpc", "max_tmpc_ts",
    "max_sknt", "max_sknt_ts", "min_tmpc", "min_tmpc_ts");
  $stData += cdf($fc, $format);

  $stData["gtim"] = totime($stData["max_sknt_ts"]);
  $stData["max_sknt_ts"] = totime($stData["max_sknt_ts"]);
  $stData["gmt_ts"] = totime($stData["gmt_ts"]);
  $stData["city"] = $Rcities[$station]["city"];
  $stData["tmpf"] = round($stData["tmpf"],0);
  $stData["dwpf"] = round($stData["dwpf"],0);
  $stData["tmpc"] = f2c($stData["tmpf"]);
  $stData["dwpc"] = f2c($stData["dwpf"]);
  $stData["sped"] = $stData["sknt"] * 1.15078;
  $stData["relh"] = relh($stData["tmpc"], $stData["dwpc"]);
  $stData["feel"] = feels_like($stData["tmpf"], $stData["relh"], $stData["sped"]);

  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  $stData["network"] = "RWIS";
  return $stData;
} // End of currentOb_rwis

//___________________________________________________________
function currentOb_awos($station){
  include('awosLoc.php');
  $dataDir = '/mesonet/data/current/ALL/';
  $fc = implode('', file($dataDir . $station .".dat") );
  $awosFormat = Array("station", "gmt_ts", "tmpf", "dwpf",
     "drct", "sknt", "gust", "alti", "phour", "vsby");
  $stData = cdf($fc, $awosFormat);

  $dataDir = '/mesonet/data/current/asos_ex/';
  $fc = @implode('', @file($dataDir ."K". $station ) );
  $format = Array("bogus", "max_tmpc", "max_tmpc_ts",
    "max_sknt", "max_sknt_ts", "min_tmpc", "min_tmpc_ts");
  $stData += cdf($fc, $format);


  $stData["city"] = $Wcities[$station]["city"];
  $stData["gmt_ts"] = totime($stData["gmt_ts"]);
  $stData["gtim"] = totime($stData["max_sknt_ts"]);
  $stData["max_sknt_ts"] = totime($stData["max_sknt_ts"]);

  $stData["tmpc"] = f2c($stData["tmpf"]);
  $stData["dwpc"] = f2c($stData["dwpf"]);
  $stData["dwpf"] = round($stData["dwpf"],0);
  $stData["tmpf"] = round($stData["tmpf"],0);
  $stData["vsby"] = round($stData["vsby"],2);
  $stData["relh"] = relh($stData["tmpc"], $stData["dwpc"]);
  $stData["sped"] = $stData["sknt"] * 1.15078;
  $stData["feel"] = feels_like($stData["tmpf"], $stData["relh"], $stData["sped"]);
  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  $stData["network"] = "AWOS";
  return $stData;
} // End of currentOb_awos

//___________________________________________________________
function currentOb_asos($station){
  include('asosLoc.php');
  $dataDir = '/mesonet/data/current/ALL/';
  $fc = implode('', file($dataDir . $station .".dat") );
  $asosFormat = Array("gmt_ts", "tmpc", "dwpc", "drct",
     "sknt", "gust", "pmsl", "alti", "metar","phour", "vsby");
  $stData = cdf($fc, $asosFormat);

  $dataDir = '/mesonet/data/current/asos_ex/';
  $fc = @implode('', @file($dataDir ."K". $station ) );
  $format = Array("bogus", "max_tmpc", "max_tmpc_ts", 
    "max_sknt", "max_sknt_ts", "min_tmpc", "min_tmpc_ts");
  $stData += cdf($fc, $format);

  $stData["tmpf"] = c2f( $stData["tmpc"] );
  $stData["dwpf"] = c2f( $stData["dwpc"] );
  $stData["city"] = $A2cities[$station]["city"];
  if (strlen($stData["city"]) == 0){
    $stData["city"] = $Ocities[$station]["city"];
  }
  $stData["gmt_ts"] = totime($stData["gmt_ts"]);

  $stData["gtim"] = totime($stData["max_sknt_ts"]);
  $stData["max_sknt_ts"] =  totime($stData["max_sknt_ts"]);
  $stData["min_tmpc_ts"] = totime($stData["min_tmpc_ts"]);
  $stData["max_tmpc_ts"] = totime($stData["max_tmpc_ts"]);

  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  $stData["network"] = "ASOS";
  $stData["tmpf"] = round($stData["tmpf"],0);
  if ($stData["vsby"] != ""){
    $stData["vsby"] = round($stData["vsby"],2);
  }
  $stData["relh"] = relh($stData["tmpc"], $stData["dwpc"]);
  $stData["dwpf"] = round($stData["dwpf"],0);
  $stData["sped"] = $stData["sknt"] * 1.15078;
  $stData["feel"] = feels_like($stData["tmpf"], $stData["relh"], $stData["sped"]);
  $stData["ts"] = $stData["gmt_ts"] - 5*3600;
  return $stData;
} // End of currentOb_asos

//============================================================
function totime($ts){
  return  mktime(substr($ts,11,13),
   substr($ts,14,16), substr($ts,17,19),
   substr($ts,5,7), substr($ts,8,10),
   substr($ts,0,4));
}

//____________________________________________________________
function cdf($fc, $format){
  $tokens = split(",", $fc);
  if (sizeof($tokens) == 0) { return Array(); }
  $stData = Array();
  while( list($key, $val) = each($format) ){
#    echo $tokens[$key] ." == ". $format[$key] ;
    $stData[$format[$key]] = $tokens[$key];
  } // End of while
  return $stData;
} // End of cdf

//___________________________________________________________
function currentOb($station){
  $asos = Array("AMW", "CID", "IOW", "BRL", "DBQ", "ALO", "MCW", "MIW",
    "DVN", "DSM", "LWD", "SPW", "EST", "SUX", "FOD", "CWI", "OTM");

  $stLength = strlen($station);
  switch ($stLength){
    case 0:
      die("Station ID is blank!");
      break;
    case 3: // ASOS or AWOS
      if ($station == "CWI" || $station == "FOD"){
        $stData = currentOb_asos($station);
      } else if ( in_array($station, $asos) ){
        $stData = currentOb_asos($station);
      } else {
        $stData = currentOb_awos($station);
        if (strlen($stData["city"]) == 0){
          $stData = currentOb_asos($station);
        }
      }
      break;
    case 4: // RWIS!
      $stData = currentOb_rwis($station);
      break;
    case 5:  // SNET!
      $stData = currentOb_snet($station);
      break;
    case 7:  // RWIS SF!
      $stData = currentOb_rwis( substr($station,0,4) );
      $stData += currentSFOb2_rwis( substr($station,0,4) );
      break;
    case 8:
      $stData = currentOb_snet( substr($station,0,5) );
      $stData += currentOb_snet2( substr($station,0,5) );
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
