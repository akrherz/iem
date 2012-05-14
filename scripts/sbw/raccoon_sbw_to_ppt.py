# -*- coding: utf-8 -*-
"""
Generate a Powerpoint file for an event

$Id: raccoon_sbw_to_ppt.py 8221 2012-05-04 14:06:49Z akrherz $:
"""
__REV__ = "$Rev: 8221 $:"
import os
os.putenv("DISPLAY", "localhost:1")
import sys
import tempfile
import getopt
import struct
import shutil
import datetime
import iemdb
import random
import psycopg2.extras
from odf.opendocument import OpenDocumentPresentation
from odf.style import Style, MasterPage, PageLayout, PageLayoutProperties
from odf.style import TextProperties, GraphicProperties, ParagraphProperties
from odf.style import DrawingPageProperties
from odf.text import P, S
from odf.draw  import Page, Frame, TextBox, Image

def test_job():
    """
    For command line testing, lets provide a dummy job
    """
    jobs = []
    jobs.append({'wfo': 'OAX', 'radar': 'OAX',
                 'sts': datetime.datetime(2012,3,28),
                 'ets': datetime.datetime(2012,3,29,12),
                 'jobid': random.randint(1,1000000)})
    return jobs

def check_for_work():
    """
    See if we have any requests to process!
    """
    MESOSITE = iemdb.connect('mesosite', bypass=True)
    mcursor = MESOSITE.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mcursor2 = MESOSITE.cursor()
    mcursor.execute("""SELECT jobid, wfo, radar, 
        sts at time zone 'UTC' as sts, 
        ets at time zone 'UTC' as ets
        from racoon_jobs WHERE processed = False""")
    jobs = []
    for row in mcursor:
        jobs.append(row)
        mcursor2.execute("""UPDATE racoon_jobs SET processed = True 
        WHERE jobid = %s""", (row[0],))
    MESOSITE.commit()
    MESOSITE.close()
    return jobs

def get_warnings(sts, ets, wfo):
    """
    Retreive an array of warnings for this time period and WFO
    """
    POSTGIS = iemdb.connect('postgis', bypass=True)
    pcursor = POSTGIS.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT phenomena, eventid, 
    issue at time zone 'UTC' as issue, 
    expire at time zone 'UTC' as expire,
    ST_Area(ST_Transform(geom,2163))/1000000.0 as area from warnings_%s WHERE
    wfo = '%s' and phenomena in ('SV','TO') and significance = 'W' and 
    gtype = 'P' and issue BETWEEN '%s+00' and '%s+00' ORDER by issue ASC""" % (
    sts.year, wfo, sts.strftime("%Y-%m-%d %H:%M"), 
    ets.strftime("%Y-%m-%d %H:%M"))
    pcursor.execute(sql)
    res = []
    for row in pcursor:
        res.append( row )
    POSTGIS.close()
    return res

def do_job(job):

    warnings = get_warnings(job['sts'], job['ets'], job['wfo'])

    os.makedirs("/tmp/%s" % (job['jobid'],))
    os.chdir("/tmp/%s" % (job['jobid'],))
    
    basefn = "%s-%s-%s-%s" % (job['wfo'], job['radar'],
                                      job['sts'].strftime("%Y%m%d%H"),
                                      job['ets'].strftime("%Y%m%d%H"))
    outputfile = "%s.odp" % (basefn,)

    doc = OpenDocumentPresentation()

    # We must describe the dimensions of the page
    pagelayout = PageLayout(name="MyLayout")
    doc.automaticstyles.addElement(pagelayout)
    pagelayout.addElement(PageLayoutProperties(margin="0pt", pagewidth="800pt",
        pageheight="600pt", printorientation="landscape"))

    # Style for the title frame of the page
    # We set a centered 34pt font with yellowish background
    titlestyle = Style(name="MyMaster-title2", family="presentation")
    titlestyle.addElement(ParagraphProperties(textalign="center"))
    titlestyle.addElement(TextProperties(fontsize="34pt"))
    titlestyle.addElement(GraphicProperties(fillcolor="#ffff99"))
    doc.styles.addElement(titlestyle)

    # Style for the title frame of the page
    # We set a centered 34pt font with yellowish background
    indexstyle = Style(name="MyMaster-title", family="presentation")
    indexstyle.addElement(ParagraphProperties(textalign="center"))
    indexstyle.addElement(TextProperties(fontsize="32pt"))
    indexstyle.addElement(GraphicProperties(fillcolor="#ffffff",
                                            stroke="none"))
    doc.styles.addElement(indexstyle)

    # Style for the photo frame
    photostyle = Style(name="MyMaster-photo", family="presentation")
    doc.styles.addElement(photostyle)

    # Every drawing page must have a master page assigned to it.
    masterpage = MasterPage(name="MyMaster", pagelayoutname=pagelayout)
    doc.masterstyles.addElement(masterpage)

    dpstyle = Style(name="dp1", family="drawing-page")
    #dpstyle.addElement(DrawingPageProperties(transitiontype="automatic",
    #   transitionstyle="move-from-top", duration="PT5S"))
    doc.automaticstyles.addElement(dpstyle)
    
    # Title slide
    page = Page(masterpagename=masterpage)
    doc.presentation.addElement(page)
    frame = Frame(stylename=indexstyle, width="720pt", height="500pt", 
                  x="40pt", y="10pt")
    page.addElement( frame )
    textbox = TextBox()
    frame.addElement(textbox)
    textbox.addElement(P(text="IEM Raccoon Report"))
    
    frame = Frame(stylename=indexstyle, width="720pt", height="500pt", 
                  x="40pt", y="150pt")
    page.addElement( frame )
    textbox = TextBox()
    frame.addElement(textbox)
    textbox.addElement(P(text="WFO: %s" % (job['wfo'],)))
    textbox.addElement(P(text="Radar: %s" % (job['radar'],)))
    textbox.addElement(P(text="Start Time: %s UTC" % (job['sts'].strftime("%d %b %Y %H"),)))
    textbox.addElement(P(text="End Time: %s UTC" % (job['ets'].strftime("%d %b %Y %H"),)))
    textbox.addElement(P(text=""))
    textbox.addElement(P(text="Raccoon Version: %s" % (__REV__,)))
    textbox.addElement(P(text="Generated on: %s" % (
                                    datetime.datetime.utcnow().strftime("%d %b %Y %H:%M %Z"))))
    textbox.addElement(P(text=""))
    textbox.addElement(P(text="Bugs/Comments/Yelling?: daryl herzmann akrherz@iastate.edu"))
    
    
    i = 0
    for warning in warnings:
        # Make Index page for the warning
        page = Page(masterpagename=masterpage)
        doc.presentation.addElement(page)
        titleframe = Frame(stylename=indexstyle, width="700pt", height="500pt", 
                       x="10pt", y="10pt")
        page.addElement(titleframe)
        textbox = TextBox()
        titleframe.addElement(textbox)
        textbox.addElement(P(text="%s.O.NEW.K%s.%s.W.%04i" % ( 
                                    job['sts'].year, job['wfo'],
                                warning['phenomena'],warning['eventid'])))
        textbox.addElement(P(text="Issue: %s UTC" % ( 
                                    warning['issue'].strftime("%d %b %Y %H:%M"),)))
        textbox.addElement(P(text="Expire: %s UTC" % ( 
                                    warning['expire'].strftime("%d %b %Y %H:%M"),)))
        textbox.addElement(P(text="Area: %.1f square km (%.1f square miles)" % ( 
                                    warning['area'], warning['area'] * 0.386102)))
        
        url = "http://iem21.local/GIS/radmap.php?"
        url += "layers[]=places&layers[]=legend&layers[]=ci&layers[]=cbw&layers[]=sbw"
        url += "&layers[]=uscounties&layers[]=bufferedlsr&lsrbuffer=15"
        url += "&vtec=%s.O.NEW.K%s.%s.W.%04i" % ( job['sts'].year, job['wfo'],
                                    warning['phenomena'],warning['eventid'])
        
        cmd = "wget -q -O %i.png '%s'" % (i, url)
        os.system(cmd)
        photoframe = Frame(stylename=photostyle, width="480pt", 
                               height="360pt", x="160pt", y="200pt")
        page.addElement(photoframe)
        href = doc.addPicture("%i.png" % (i,))
        photoframe.addElement(Image(href=href))
        i += 1
        
        times = []
        now = warning['issue']
        while now < warning['expire']:
            times.append( now )
            now += datetime.timedelta(minutes=15)
        times.append( warning['expire'] - datetime.timedelta(minutes=1))
        
        for now in times:    
            page = Page(stylename=dpstyle, masterpagename=masterpage)
            doc.presentation.addElement(page)
            titleframe = Frame(stylename=titlestyle, width="720pt", height="56pt", 
                           x="40pt", y="10pt")
            page.addElement(titleframe)
            textbox = TextBox()
            titleframe.addElement(textbox)
            textbox.addElement(P(text="%s.W.%04i Time: %s UTC" % ( 
                                    warning['phenomena'],warning['eventid'],
                                    now.strftime("%d %b %Y %H%M"))))
            
            url = "http://iem21.local/GIS/radmap.php?"
            url += "layers[]=ridge&ridge_product=N0Q&ridge_radar=%s&" % (job['radar'],)
            url += "layers[]=sbw&layers[]=sbwh&layers[]=uscounties&"
            url += "layers[]=lsrs&ts2=%s&" % (
                    (now + datetime.timedelta(minutes=15)).strftime("%Y%m%d%H%M"),)
            url += "vtec=%s.O.NEW.K%s.%s.W.%04i&ts=%s" % ( job['sts'].year, job['wfo'],
                                    warning['phenomena'],warning['eventid'],
                                    now.strftime("%Y%m%d%H%M"))
        
            cmd = "wget -q -O %i.png '%s'" % (i, url)
            os.system(cmd)
            photoframe = Frame(stylename=photostyle, width="640pt", 
                               height="480pt", x="80pt", y="70pt")
            page.addElement(photoframe)
            href = doc.addPicture("%i.png" % (i,))
            photoframe.addElement(Image(href=href))
            i += 1

    doc.save(outputfile)
    del doc
    cmd = "unoconv -f ppt %s" % (outputfile,)
    os.system( cmd )
    print "%s.ppt" % (basefn,)
    if os.path.isfile("%s.ppt" % (basefn,)):
        print 'Here!'
        shutil.copyfile("%s.ppt" % (basefn,), "/mesonet/share/pickup/raccoon/%s.ppt" % (basefn,))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        jobs = test_job()
    else:
        jobs = check_for_work()
    if len(jobs) == 0:
        sys.exit()
    for job in jobs:
        do_job(job)
