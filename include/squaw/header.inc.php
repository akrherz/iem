<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <title>Squaw Creek Flood Modeling</title>
  <link rel="stylesheet" type="text/css" href="<?php echo $_BASEURL; ?>/css/main.css" />
</head>
<body>

<div id="header">
<h2>Squaw Creek Flood Prediction System</h2>
</div>

<div id="mainNavOuter">
<div id="mainNav">
<div id="mainNavInner">

<ul>
 <li id="mainFirst<?php if ($THISPAGE == "homepage") echo "-active"; ?>"><a href="<?php echo $rooturl; ?>squaw/">Homepage</a></li>
 <li id="main<?php if ($THISPAGE == "model") echo "-active"; ?>"><a href="<?php echo $rooturl; ?>/squaw/model/index.phtml">Run Model</a></li>
 <li id="main<?php if ($THISPAGE == "scenario") echo "-active"; ?>"><a href="<?php echo $rooturl; ?>/squaw/scenario/index.phtml">Scenario Editor</a></li>
 <li id="mainLast<?php if ($THISPAGE == "storm") echo "-active"; ?>"><a href="<?php echo $rooturl; ?>/squaw/storm/index.phtml">Storm Editor</a></li>
</ul>

</div></div></div>
