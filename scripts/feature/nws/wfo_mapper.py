import psycopg2
import datetime
#import numpy as np
from pyiem.plot import MapPlot

text = """  KWAL   | 000
 KARS   | 111
 KBWL   | 779
 KEHU   | ADA
 KARB   | ADM
 KVUY   | ADM
 KBCQ   | ADM
 KCRH   | ADM
 KBTV   | AFD
 KBOX   | AFD
 KBGM   | AFD
 KHUN   | AFD
 KILN   | AFD
 KDLH   | AFD
 KALY   | AFD
 KCTP   | AFD
 KSJT   | AFD
 KBUF   | AFD
 KICT   | AFM
 KGYX   | AFM
 KTOP   | AFM
 KCAE   | AFM
 KOHX   | AWO
 KTSA   | AWU
 KAWN   | BKN
 KEPZ   | CF6
 KVEF   | CF6
 KPDT   | CF6
 KRIW   | CF6
 KEWX   | CF6
 KBMX   | CF6
 KPAH   | CF6
 KSTO   | CF6
 KOUN   | CF6
 KOTX   | CF6
 KFWD   | CF6
 KMPX   | CF6
 KMLB   | CF6
 KGRB   | CF6
 KHGX   | CF6
 KLOX   | CF6
 KLKN   | CF6
 KEYW   | CF6
 KLCH   | CF6
 KJAN   | CF6
 KIWX   | CF6
 KEKA   | CGR
 KSEW   | CGR
 KMIA   | CHG
 KFFC   | CLI
 KABR   | CLI
 KAMA   | CLI
 KBIS   | CLI
 KBOI   | CLI
 KBRO   | CLI
 KBYZ   | CLI
 KCAR   | CLI
 KCYS   | CLI
 KEAX   | CLI
 KFSD   | CLI
 KGRR   | CLI
 KIGM   | CLI
 KIND   | CLI
 KLMK   | CLI
 KLRD   | CLI
 KLRF   | CLI
 KLWX   | CLI
 KMEG   | CLI
 KMFL   | CLI
 KMKX   | CLI
 KOAX   | CLI
 KPBZ   | CLI
 KPHI   | CLI
 KPIH   | CLI
 KPUB   | CLI
 KRNK   | CLI
 KSHV   | CLI
 KSMX   | CLI
 KTBW   | CLI
 KWNP   | CUR
 KXXX   | CWF
 KABQ   | DSM
 KZBW   | DSM
 KZDV   | DSM
 KFGZ   | DSM
 KZAU   | DSM
 KZAN   | DSM
 KZAB   | DSM
 KMRX   | DSM
 KEEO   | DSM
 KMCO   | DSM
 KZJX   | DSM
 KZKC   | DSM
 KZME   | DSM
 KZMA   | DSM
 KZDC   | DSM
 KZLA   | DSM
 KZLC   | DSM
 KUNR   | DSM
 KZTL   | DSM
 KZSE   | DSM
 KZOB   | DSM
 KROA   | DSM
 KZFW   | DSM
 KZOA   | DSM
 KZHN   | DSM
 KZHU   | DSM
 KREO   | DSM
 KZNY   | DSM
 KZID   | DSM
 KZMP   | DSM
 KNEC   | EQR
 KKRF   | FFG
 KORN   | FFG
 KTUA   | FFG
 KALR   | FFG
 KRHA   | FFG
 KFWR   | FFG
 KPTR   | FOP
 KMKE   | FTM
 KMWI   | FWO
 KSGX   | FWO
 KDTX   | GLF
 KWOH   | HML
 KSLC   | HMT
 KRSA   | HP2
 KLOT   | HRR
 KCRP   | HRR
 KSGF   | HRR
 KILX   | HWR
 KLAX   | HYM
 KFAT   | HYM
 KSFO   | HYM
 KSAN   | HYM
 KSAC   | HYM
 KTCG   | ICE
 KBOU   | IKA
 KARX   | IKA
 KDDC   | IKA
 KSSM   | IOB
 KDTW   | IOB
 KMAF   | KPA
 KMSC   | LAS
 KDEN   | LCO
 KLBF   | LDM
 KSTC   | MAN
 KAPG   | MAN
 KLUB   | MIS
 KRAH   | MIS
 KGSO   | MIS
 KLBB   | MIS
 KGID   | MIS
 KWNO   | MMG
 KWNB   | MOB
 KWNA   | MON
 KACR   | MON
 KSFM   | MON
 KGUM   | MON
 KAFG   | MON
 KAJK   | MON
 KHFO   | MON
 KNHO   | MON
 KCRW   | MOS
 KCKB   | MOS
 KHTS   | MOS
 KDAB   | MSM
 KKEY   | NOW
 KWNJ   | OAV
 KNHC   | OFF
 KWNM   | OFF
 KMTR   | OMR
 KAKQ   | OMR
 KCLE   | OMR
 KFGF   | OPU
 KCHS   | OPU
 KGGW   | OPU
 KWBJ   | OSB
 KJAX   | OSO
 KREV   | OSO
 KMFR   | OSO
 KLIX   | OSO
 KOKX   | OSO
 KTAE   | OSO
 KTFX   | OSO
 KTWC   | OSO
 KJKL   | OSO
 KILM   | OSO
 KMSO   | OSO
 KRLX   | OSO
 KGJT   | PFM
 KGLD   | PFM
 KLSX   | PFM
 KAPX   | PFM
 KWNC   | POE
 KWNH   | QPG
 KEVV   | RER
 KALB   | RER
 KPSR   | RTP
 KDVN   | RVA
 KDMX   | RVA
 KSTR   | RVF
 KTAR   | RVF
 KTIR   | RVF
 KPQR   | RVM
 KISN   | SCD
 KSCS   | SCN
 KNES   | SCP
 KMSR   | SCV
 KMOB   | SFT
 KKCI   | SIG
 KWNS   | STA
 KHQA   | STQ
 KLAS   | SVS
 KMHX   | TID
 KWBC   | TPT
 KNCF   | TST
 KSPC   | TST
 KSJU   | TST
 KBHM   | WRK
 KSAT   | WRK
 KLZK   | WRK
 KNCF   | WTS
 KWBN   | XF0
 KHNX   | ZFP
 KGSP   | ZFP
 KMQT   | ZFP
 KXXX   | ZFP
  PAOM   | ABV
 PABE   | ABV
 PAKN   | ABV
 PASN   | ABV
 PARH   | ADM
 PABR   | CLI
 PAJK   | CWF
 PGUM   | CWF
 PAWU   | FA8
 PTTP   | FZL
 PHTO   | FZL
 PAOT   | FZL
 PACD   | FZL
 PKMR   | FZL
 PHLI   | FZL
 PTKR   | FZL
 PKMJ   | FZL
 PADQ   | FZL
 PGTW   | LON
 PGSN   | MTR
 PAYA   | NOW
 PANT   | NOW
 PAVD   | NOW
 PAFC   | OFF
 PTYA   | OMR
 PAVW   | OMR
 PTKK   | OMR
 PAJN   | OSO
 PHFO   | OSO
 PACR   | RVF
 PAMC   | SCD
 PAFA   | SCD
 PANC   | SHP
 PTSA   | SSM
 PAER   | STQ
 PALU   | STQ
 PAAQ   | TST
 PHEB   | TST
 PAFG   | ZFP"""

from pyiem.network import Table

nt = Table("WFO")

data = {}
labels = {}
uniq = []
for line in text.split("\n"):
    tokens = line.replace(" ", "").split("|")
    wfo = tokens[0][1:]
    if tokens[0][0] == 'P':
        wfo = tokens[0]
    key = "%s" % (tokens[1], )
    if not nt.sts.has_key(wfo):
        continue
    # P
    wfo = tokens[0][1:]
    if not key in uniq:
        uniq.append( key )
    data[ wfo ] = len(uniq) -1
    labels[ wfo ] = key
    if wfo == 'JSJ':
        labels['SJU'] = labels['JSJ']

bins = range(len(uniq)+1)
uniq.append('')

p = MapPlot(sector='nws', axisbg='white',
                 title="2009-2013 Most Frequently issued non-SHEF 3char AWIPS ID",
                 subtitle='RR* products were excluded from this analysis')
p.fill_cwas(data, bins=bins, labels=labels, lblformat='%s', clevlabels=uniq)
p.postprocess(filename='test.png')
#import iemplot
#iemplot.makefeature('test')
