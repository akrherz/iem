<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/forms.php";
// 27 Feb 2025 still being used...
$pil = strtoupper(get_str404("pil", 'AFDDMX', 6));
$cnt = get_int404("cnt", 1);
$center = get_str404("center", "", 4);
$sdate = get_str404("sdate", '');
$edate = get_str404("edate", '');

header("Location: /cgi-bin/afos/retrieve.py?pil={$pil}&center={$center}&limit={$cnt}&sdate={$sdate}&edate={$edate}");
