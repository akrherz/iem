# -*- coding: utf-8 -*-
"""Generate a Powerpoint file for an event.

This script looks for queued jobs within the database and runs them
sequentially each minute"""

import sys
import shutil
import datetime
import subprocess
import random
import os

import psycopg2.extras
from odf.opendocument import OpenDocumentPresentation
from odf.style import Style, MasterPage, PageLayout, PageLayoutProperties
from odf.style import TextProperties, GraphicProperties, ParagraphProperties
from odf.text import P
from odf.draw import Page, Frame, TextBox, Image
from pyiem.util import get_dbconn, logger

os.putenv("DISPLAY", "localhost:1")

LOG = logger()
__REV__ = "28Jan2020"
TMPDIR = "/mesonet/tmp"
SUPER_RES = datetime.datetime(2010, 3, 1)


def test_job():
    """For command line testing, lets provide a dummy job"""
    jobs = []
    jobs.append(
        {
            "wfo": "FSD",
            "radar": "FSD",
            "wtype": "SV,TO",
            "sts": datetime.datetime(2003, 6, 24, 2),
            "ets": datetime.datetime(2003, 6, 24, 4),
            "jobid": random.randint(1, 1000000),
            "nexrad_product": "N0U",
        }
    )
    return jobs


def add_job(row):
    """Add back a job"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    LOG.info("setting racoon jobid: %s back to unprocessed", row["jobid"])
    mcursor.execute(
        """
        UPDATE racoon_jobs SET processed = False
        WHERE jobid = %s
    """,
        (row["jobid"],),
    )
    mcursor.close()
    pgconn.commit()


def check_for_work():
    """See if we have any requests to process!"""
    pgconn = get_dbconn("mesosite", user="nobody")
    mcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mcursor2 = pgconn.cursor()
    mcursor.execute(
        """SELECT jobid, wfo, radar,
        sts at time zone 'UTC' as sts,
        ets at time zone 'UTC' as ets, nexrad_product, wtype
        from racoon_jobs WHERE processed = False"""
    )
    jobs = []
    for row in mcursor:
        jobs.append(row)
        mcursor2.execute(
            """UPDATE racoon_jobs SET processed = True
        WHERE jobid = %s""",
            (row[0],),
        )
    pgconn.commit()
    pgconn.close()
    return jobs


def get_warnings(sts, ets, wfo, wtypes):
    """Retreive an array of warnings for this time period and WFO"""
    tokens = wtypes.split(",")
    tokens.append("ZZZ")
    phenomenas = str(tuple(tokens))
    pgconn = get_dbconn("postgis", user="nobody")
    pcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """
    WITH stormbased as (
        SELECT phenomena, eventid, issue, expire,
        ST_Area(ST_Transform(geom,2163))/1000000.0 as polyarea
        from sbw_%s WHERE issue BETWEEN '%s+00' and '%s+00' and
        wfo = '%s' and phenomena in %s and significance = 'W'
        and status = 'NEW'
    ), countybased as (
        SELECT phenomena, eventid,
        sum(ST_Area(ST_Transform(u.geom,2163))/1000000.0) as countyarea
        from warnings_%s w JOIN ugcs u on (u.gid = w.gid) WHERE
        issue BETWEEN '%s+00' and '%s+00' and
        w.wfo = '%s' and phenomena in %s and significance = 'W'
        GROUP by phenomena, eventid
    )

    SELECT s.phenomena, s.eventid,
    s.issue at time zone 'UTC' as issue,
    s.expire at time zone 'UTC' as expire, s.polyarea,
    c.countyarea from stormbased s JOIN countybased c
    on (c.eventid = s.eventid and c.phenomena = s.phenomena)
    """ % (
        sts.year,
        sts.strftime("%Y-%m-%d %H:%M"),
        ets.strftime("%Y-%m-%d %H:%M"),
        wfo,
        phenomenas,
        sts.year,
        sts.strftime("%Y-%m-%d %H:%M"),
        ets.strftime("%Y-%m-%d %H:%M"),
        wfo,
        phenomenas,
    )
    pcursor.execute(sql)
    res = []
    for row in pcursor:
        res.append(row)
    pgconn.close()
    return res


def do_job(job):
    """Do something"""
    warnings = get_warnings(job["sts"], job["ets"], job["wfo"], job["wtype"])

    mydir = "%s/%s" % (TMPDIR, job["jobid"])
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    os.chdir(mydir)

    basefn = "%s-%s-%s-%s-%s" % (
        job["wfo"],
        job["wtype"].replace(",", "_"),
        job["radar"],
        job["sts"].strftime("%Y%m%d%H"),
        job["ets"].strftime("%Y%m%d%H"),
    )
    outputfile = "%s.odp" % (basefn,)

    doc = OpenDocumentPresentation()

    # We must describe the dimensions of the page
    pagelayout = PageLayout(name="MyLayout")
    doc.automaticstyles.addElement(pagelayout)
    pagelayout.addElement(
        PageLayoutProperties(
            margin="0pt",
            pagewidth="800pt",
            pageheight="600pt",
            printorientation="landscape",
        )
    )

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
    indexstyle.addElement(TextProperties(fontsize="28pt"))
    indexstyle.addElement(
        GraphicProperties(fillcolor="#ffffff", stroke="none")
    )
    doc.styles.addElement(indexstyle)

    # Style for the photo frame
    photostyle = Style(name="MyMaster-photo", family="presentation")
    doc.styles.addElement(photostyle)

    # Every drawing page must have a master page assigned to it.
    masterpage = MasterPage(name="MyMaster", pagelayoutname=pagelayout)
    doc.masterstyles.addElement(masterpage)

    dpstyle = Style(name="dp1", family="drawing-page")
    # dpstyle.addElement(DrawingPageProperties(transitiontype="automatic",
    #   transitionstyle="move-from-top", duration="PT5S"))
    doc.automaticstyles.addElement(dpstyle)

    # Title slide
    page = Page(masterpagename=masterpage)
    doc.presentation.addElement(page)
    frame = Frame(
        stylename=indexstyle, width="720pt", height="500pt", x="40pt", y="10pt"
    )
    page.addElement(frame)
    textbox = TextBox()
    frame.addElement(textbox)
    textbox.addElement(P(text="IEM Raccoon Report"))

    frame = Frame(
        stylename=indexstyle,
        width="720pt",
        height="500pt",
        x="40pt",
        y="150pt",
    )
    page.addElement(frame)
    textbox = TextBox()
    frame.addElement(textbox)
    textbox.addElement(P(text="WFO: %s" % (job["wfo"],)))
    textbox.addElement(
        P(
            text=("Radar: %s Product: %s" "")
            % (job["radar"], job["nexrad_product"])
        )
    )
    textbox.addElement(P(text="Phenomenas: %s" % (job["wtype"],)))
    textbox.addElement(
        P(text="Start Time: %s UTC" % (job["sts"].strftime("%d %b %Y %H"),))
    )
    textbox.addElement(
        P(text="End Time: %s UTC" % (job["ets"].strftime("%d %b %Y %H"),))
    )
    textbox.addElement(P(text=""))
    textbox.addElement(P(text="Raccoon Version: %s" % (__REV__,)))
    textbox.addElement(
        P(
            text="Generated on: %s"
            % (datetime.datetime.utcnow().strftime("%d %b %Y %H:%M %Z"))
        )
    )
    textbox.addElement(P(text=""))
    textbox.addElement(
        P(text="Bugs/Comments/Yelling?: daryl herzmann akrherz@iastate.edu")
    )

    i = 0
    for warning in warnings:
        # Make Index page for the warning
        page = Page(masterpagename=masterpage)
        doc.presentation.addElement(page)
        titleframe = Frame(
            stylename=indexstyle,
            width="700pt",
            height="500pt",
            x="10pt",
            y="10pt",
        )
        page.addElement(titleframe)
        textbox = TextBox()
        titleframe.addElement(textbox)
        textbox.addElement(
            P(
                text="%s.O.NEW.K%s.%s.W.%04i"
                % (
                    job["sts"].year,
                    job["wfo"],
                    warning["phenomena"],
                    warning["eventid"],
                )
            )
        )
        textbox.addElement(
            P(
                text="Issue: %s UTC"
                % (warning["issue"].strftime("%d %b %Y %H:%M"),)
            )
        )
        textbox.addElement(
            P(
                text="Expire: %s UTC"
                % (warning["expire"].strftime("%d %b %Y %H:%M"),)
            )
        )
        textbox.addElement(
            P(
                text="Poly Area: %.1f sq km (%.1f sq mi) [%.1f%% vs County]"
                % (
                    warning["polyarea"],
                    warning["polyarea"] * 0.386102,
                    warning["polyarea"] / warning["countyarea"] * 100.0,
                )
            )
        )
        textbox.addElement(
            P(
                text="County Area: %.1f square km (%.1f square miles)"
                % (warning["countyarea"], warning["countyarea"] * 0.386102)
            )
        )

        url = (
            "http://iem.local/GIS/radmap.php?"
            "layers[]=places&layers[]=legend&layers[]=ci&layers[]=cbw"
            "&layers[]=sbw&layers[]=uscounties&layers[]=bufferedlsr"
            "&lsrbuffer=15"
        )
        url += "&vtec=%s.O.NEW.K%s.%s.W.%04i" % (
            job["sts"].year,
            job["wfo"],
            warning["phenomena"],
            warning["eventid"],
        )

        cmd = "wget -q -O %i.png '%s'" % (i, url)
        os.system(cmd)
        photoframe = Frame(
            stylename=photostyle,
            width="480pt",
            height="360pt",
            x="160pt",
            y="200pt",
        )
        page.addElement(photoframe)
        href = doc.addPicture("%i.png" % (i,))
        photoframe.addElement(Image(href=href))
        i += 1

        times = []
        now = warning["issue"]
        while now < warning["expire"]:
            times.append(now)
            now += datetime.timedelta(minutes=15)
        times.append(warning["expire"] - datetime.timedelta(minutes=1))

        for now in times:
            page = Page(stylename=dpstyle, masterpagename=masterpage)
            doc.presentation.addElement(page)
            titleframe = Frame(
                stylename=titlestyle,
                width="720pt",
                height="56pt",
                x="40pt",
                y="10pt",
            )
            page.addElement(titleframe)
            textbox = TextBox()
            titleframe.addElement(textbox)
            textbox.addElement(
                P(
                    text="%s.W.%04i Time: %s UTC"
                    % (
                        warning["phenomena"],
                        warning["eventid"],
                        now.strftime("%d %b %Y %H%M"),
                    )
                )
            )

            if job["nexrad_product"] == "N0U":
                if now < SUPER_RES:
                    n0qn0r = "N0V"
                else:
                    n0qn0r = "N0U"
            else:
                if now < SUPER_RES:
                    n0qn0r = "N0R"
                else:
                    n0qn0r = "N0Q"

            url = "http://iem.local/GIS/radmap.php?"
            url += "layers[]=ridge&ridge_product=%s&ridge_radar=%s&" % (
                n0qn0r,
                job["radar"],
            )
            url += "layers[]=sbw&layers[]=sbwh&layers[]=uscounties&"
            url += "layers[]=lsrs&ts2=%s&" % (
                (now + datetime.timedelta(minutes=15)).strftime("%Y%m%d%H%M"),
            )
            url += "vtec=%s.O.NEW.K%s.%s.W.%04i&ts=%s" % (
                job["sts"].year,
                job["wfo"],
                warning["phenomena"],
                warning["eventid"],
                now.strftime("%Y%m%d%H%M"),
            )

            cmd = "wget -q -O %i.png '%s'" % (i, url)
            os.system(cmd)
            photoframe = Frame(
                stylename=photostyle,
                width="640pt",
                height="480pt",
                x="80pt",
                y="70pt",
            )
            page.addElement(photoframe)
            href = doc.addPicture("%i.png" % (i,))
            photoframe.addElement(Image(href=href))
            i += 1

    doc.save(outputfile)
    del doc
    cmd = "unoconv -f ppt %s" % (outputfile,)
    subprocess.call(cmd, shell=True)
    pptfn = "%s.ppt" % (basefn,)
    LOG.info("Generated %s with %s slides", pptfn, i)
    if os.path.isfile(pptfn):
        LOG.info("...copied to webfolder")
        shutil.copyfile(pptfn, "/mesonet/share/pickup/raccoon/%s" % (pptfn,))
        # Cleanup
        os.chdir(TMPDIR)
        subprocess.call("rm -rf %s" % (job["jobid"],), shell=True)
    else:
        LOG.info("Uh oh, no output file, lets kill soffice.bin")
        subprocess.call("pkill --signal 9 soffice.bin", shell=True)
        add_job(job)


def main(argv):
    """Do main"""
    if len(argv) == 2:
        jobs = test_job()
    else:
        jobs = check_for_work()
    if not jobs:
        sys.exit()
    for job in jobs:
        do_job(job)


if __name__ == "__main__":
    main(sys.argv)
