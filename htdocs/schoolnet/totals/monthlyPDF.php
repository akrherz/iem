<?php 
  define('FPDF_FONTPATH','pdf/font/');
  require('pdf/fpdf.php');

class PDF extends FPDF
{
function Footer()
{
    //Position at 1.5 cm from bottom
    $this->SetY(-15);
    //Arial italic 8
    $this->SetFont('Arial','I',8);
    //Page number
    $this->Cell(0,10,'Page '.$this->PageNo().'/{nb}',0,0,'C');
}
function Header()
{
    global $station;
    global $Scities;
    //Logo
    $this->Image('images/cipco.png',10,8,43);
    //Arial bold 15
    $this->SetFont('Arial','B',15);
    //Move to the right
    $this->Cell(80);
    //Title
    $this->Cell(50,10,'Daily Totals for '.$Scities[$station]['city'],0,0,'C');
    //Line break
    $this->Ln(20);
}// End Header

//Load data
function LoadData()
{
  global $station, $month;
  $c0 = pg_connect('db1.mesonet.agron.iastate.edu', 5432, 'snet');
  $q0 = "SELECT *, to_char(valid, 'Dy Mon DD') as dvalid from t2002_daily 
    WHERE station = '". $station ."' 
    and extract(month from valid) = $month ORDER by valid";
  $r0 = pg_exec($c0, $q0);

 $data=array();
 for( $i=0; $row = @pg_fetch_array($r0,$i); $i++){
   $data[]=$row;
  }
 return $data;
} // End of LoadData()

function WriteHTML($html)
{
    //HTML parser
    $html=str_replace("\n",' ',$html);
    $a=preg_split('/<(.*)>/U',$html,-1,PREG_SPLIT_DELIM_CAPTURE);
    foreach($a as $i=>$e)
    {
        if($i%2==0)
        {
            //Text
            if($this->HREF)
                $this->PutLink($this->HREF,$e);
            else
                $this->Write(5,$e);
        }
        else
        {
            //Tag
            if($e{0}=='/')
                $this->CloseTag(strtoupper(substr($e,1)));
            else
            {
                //Extract properties
                $a2=split(' ',$e);
                $tag=strtoupper(array_shift($a2));
                $prop=array();
                foreach($a2 as $v)
                    if(ereg('^([^=]*)=["\']?([^"\']*)["\']?$',$v,$a3))
                        $prop[strtoupper($a3[1])]=$a3[2];
                $this->OpenTag($tag,$prop);
            }
        }
    }
}

//Colored table
function FancyTable($header,$data)
{
        //Colors, line width and bold font
        $this->SetFillColor(255,0,0);
        $this->SetTextColor(255);
        $this->SetDrawColor(128,0,0);
        $this->SetLineWidth(.3);
        $this->SetFont('','B');
        //Header
        $w=array(40,35,40,45);
        for($i=0;$i<count($header);$i++)
                $this->Cell($w[$i],7,$header[$i],1,0,'C',1);
        $this->Ln();
        //Color and font restoration
        $this->SetFillColor(224,235,255);
        $this->SetTextColor(0);
        $this->SetFont('');
        //Data
        $fill=0;
        foreach($data as $row)
        {
                $this->Cell($w[0],6,$row['dvalid'],'LR',0,'L',$fill);
                $this->Cell($w[1],6,number_format($row[2]),'LR',0,'R',$fill);
                $this->Cell($w[2],6,number_format($row[3]),'LR',0,'R',$fill);
                $this->Cell($w[3],6,$row[4],'LR',0,'R',$fill);
                $this->Cell($w[4],6,number_format($row[5]),'LR',0,'R',$fill);
                $this->Ln();
                $fill=!$fill;
        }
        $this->Cell(array_sum($w),0,'','T');
}

function OpenTag($tag,$prop)
{
    //Opening tag
    if($tag=='B' or $tag=='I' or $tag=='U')
        $this->SetStyle($tag,true);
    if($tag=='A')
        $this->HREF=$prop['HREF'];
    if($tag=='BR')
        $this->Ln(5);
}

function CloseTag($tag)
{
    //Closing tag
    if($tag=='B' or $tag=='I' or $tag=='U')
        $this->SetStyle($tag,false);
    if($tag=='A')
        $this->HREF='';
}

function SetStyle($tag,$enable)
{
    //Modify style and select corresponding font
    $this->$tag+=($enable ? 1 : -1);
    $style='';
    foreach(array('B','I','U') as $s)
        if($this->$s>0)
            $style.=$s;
    $this->SetFont('',$style);
}

function PutLink($URL,$txt)
{
    //Put a hyperlink
    $this->SetTextColor(0,0,255);
    $this->SetStyle('U',true);
    $this->Write(5,$txt,$URL);
    $this->SetStyle('U',false);
    $this->SetTextColor(0);
}

} // End of FPDF


include("../../include/snetLoc.php"); 
if (strlen($station) == 0){
 $station = 'SKCI4';
}
if (strlen($month) == 0){
 $month = 10;
}

$html='Monthly Report: '.$Scities[$station]['city'] .'<BR>This data is
  provided as-is, blah blah.  See our 
  <A HREF="http://mesonet.agron.iastate.edu">website</A> for more info';

$pdf=new PDF();
$pdf->Open();
$pdf->AliasNbPages();
$pdf->SetFont('Arial','',12);
$header = array('Date', 'High', 'Low', 'Precip', 'Reports');

$data = $pdf->LoadData();
$pdf->AddPage();
$pdf->FancyTable($header,$data);
$pdf->AddPage();
$pdf->Cell(40,10,'This is text on page 2!!');
$pdf->Ln(20);
$pdf->WriteHTML($html);
$pdf->Output();
?>
