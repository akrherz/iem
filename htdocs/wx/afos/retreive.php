<?php
// 1 Aug 2022 still being used...
$pil = isset($_REQUEST["pil"]) ? strtoupper($_REQUEST["pil"]) : 'AFDDMX';
$cnt = isset($_REQUEST["cnt"]) ? intval($_REQUEST["cnt"]): 1;
$center = isset($_REQUEST["center"]) ? substr($_REQUEST["center"],0,4): "";
$sdate = isset($_REQUEST["sdate"]) ? $_REQUEST["sdate"] : '';
$edate = isset($_REQUEST["edate"]) ? $_REQUEST["edate"] : '';

header("Location: /cgi-bin/afos/retrieve.py?pil={$pil}&center={$center}&limit={$cnt}&sdate={$sdate}&edate={$edate}");
