<?php
include("../../config/settings.inc.php");
require_once "$rootpath/include/excel/Writer.php";

// What is requested of us!
$report = isset($_GET["report"])? substr($_GET["report"],0,2): "01";
$station = isset($_GET["station"])? strtolower( substr($_GET["station"],0,6) ): "ia0200";

// Creating a workbook
$workbook = new Spreadsheet_Excel_Writer();
// sending HTTP headers
$workbook->send('test.xls');
// Creating a worksheet
$worksheet =& $workbook->addWorksheet('My first worksheet');

$splitter = Array(
 "01" => Array(0, 4, 19, 24, 31, 35, 44, 53, 62, 72, 80, 120),
 "02" => Array(0, 7, 12, 18, 120),
 "03" => Array(0, 7, 14, 21, 28, 35, 42, 49, 56, 120),
 "04" => Array(0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 120),
 "05" => Array(0, 4, 10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 120),
 "06" => Array(0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 120),
 "07" => Array(0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 120),
 "08" => Array(0, 5, 120),
 "09" => Array(0, 8, 14, 18, 22, 36, 40, 44, 120),
 "10" => Array(0, 8, 14, 18, 22, 36, 40, 44, 120),
 "11" => Array(0, 8, 14, 18, 22, 36, 40, 44, 120),
 "12" => Array(0, 8, 14, 18, 22, 36, 40, 44, 120),
 "13" => Array(0, 8, 14, 18, 22, 36, 40, 44, 120),
 "14" => Array(0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 60, 67, 73, 79, 85, 91, 120),
 "15" => Array(0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 60, 67, 73, 79, 85, 91, 120),
 "16" => Array(0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 60, 67, 73, 79, 85, 91, 120),
 "17" => Array(0, 5, 11, 17, 23, 29, 35, 41, 47, 53, 59, 65, 71, 77, 83, 89, 120),
 "18" => Array(0, 5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 75, 82, 89, 96, 120),
 "19" => Array(0, 5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 75, 82, 89, 96, 120),
 "20" => Array(0, 6, 12, 18, 24, 30, 36, 42, 51, 57, 63, 69, 75, 120),
 "21" => Array(0, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 120),
 "22" => Array(0, 5, 13, 18, 23, 28, 120),
 "23" => Array(0, 5, 13, 18, 23, 28, 120),
 "24" => Array(0, 6, 14, 21, 30, 37, 46, 53, 62, 120),

);


$fc = file("reports/${station}_${report}.txt");
while (list ($line_num, $line) = each ($fc)) {
 if (sizeof($line) == 0) continue;

 if ($line[0] == '#') {
  $worksheet->write($line_num, 0, $line);
  continue;
 }

 $ar = $splitter[$report];
 for ($i=1;$i<sizeof($ar);$i++)
 {
   $token = substr($line,$ar[$i-1],$ar[$i]-$ar[$i-1]);
   $worksheet->write($line_num, $i-1, trim($token) );
 }
}



// Let's send the file
$workbook->close();
?>
