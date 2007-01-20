<?php
  include("$rootpath/include/catch_phrase.php");
  srand ((float) microtime() * 10000000);
  $t = array_rand($phrases);
  $phrase = $phrases[$t];

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
 <title><?php echo isset($TITLE) ? $TITLE: "Iowa Environmental Mesonet"; ?></title>
 <link rel="stylesheet" type="text/css" href="<?php echo $rooturl; ?>/css/main.css?v=0.0.1" />
 <?php if (isset($REFRESH)){ echo $REFRESH; } ?>
 <?php if (isset($HEADEXTRA)){ echo $HEADEXTRA;} ?>
</head>
<body <?php if (isset($BODYEXTRA)){ echo $BODYEXTRA;} ?>>
<?php include("$rootpath/include/webring.html"); ?>
<div id="iem-main">
<div id="iem-header">
<div id="iem-header-logo">
<a href="<?php echo $rooturl; ?>/"><img src="<?php echo $rooturl; ?>/images/logo_small.gif" alt="IEM" /></a>
</div>
                                                                                
<div id="iem-header-title">
<h3>Iowa Environmental Mesonet</h3>
<h4>Iowa State University Department of Agronomy</h4>
</div>
                                                                                
<div id="iem-header-items">
<i><?php echo $phrase; ?></i>
</div>

<ul id="iemmenu">
<li><a href="<?php echo $rooturl; ?>/archive/">&middot;Archive</a></li>
<li><a href="<?php echo $rooturl; ?>/current/">&middot;Current</a></li>
<li><a href="<?php echo $rooturl; ?>/climate/">&middot;Climatology</a></li>
<li><a href="<?php echo $rooturl; ?>/climodat/">&middot;Climodat</a></li>
<li><a href="<?php echo $rooturl; ?>/cool/">&middot;Cool Stuff</a></li>
<li><a href="<?php echo $rooturl; ?>/sites/locate.php">&middot;IEM Sites</a></li>
<li><a href="<?php echo $rooturl; ?>/GIS/">&middot;GIS</a></li>
<li><a href="<?php echo $rooturl; ?>/info.php">&middot;Info</a></li>
<li><a href="<?php echo $rooturl; ?>/QC/">&middot;Quality Control</a></li>
</ul> 
 
</div><!-- End of iem-header -->
<div id="iem-content">
