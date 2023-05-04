# -*- coding: utf-8 -*-
"""Generate a Powerpoint file for an event.

This script looks for queued jobs within the database and runs them
sequentially each minute"""

import datetime
import os
import random
import shutil
import subprocess
import sys

import psycopg2.extras
from odf.draw import Frame, Image, Page, TextBox
from odf.opendocument import OpenDocumentPresentation
from odf.style import (
    GraphicProperties,
    MasterPage,
    PageLayout,
    PageLayoutProperties,
    ParagraphProperties,
    Style,
    TextProperties,
)
from odf.text import P
from pyiem.util import get_dbconn, logger, utc

os.putenv("DISPLAY", "localhost:1")

LOG = logger()
__REV__ = "06Jun2022"
TMPDIR = "/mesonet/tmp"
SUPER_RES = datetime.datetime(2010, 3, 1)
N0B_SWITCH = datetime.datetime(2022, 5, 16)


def test_job():
    """For command line testing, lets provide a dummy job"""
    return [
        {
            "wfo": "FSD",
            "radar": "FSD",
            "wtype": "SV,TO",
            "sts": datetime.datetime(2003, 6, 24, 2),
            "ets": datetime.datetime(2003, 6, 24, 4),
            "jobid": random.randint(1, 1000000),
            "nexrad_product": "N0U",
        }
    ]


def add_job(row):
    """Add back a job"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    LOG.warning("setting racoon jobid: %s back to unprocessed", row["jobid"])
    mcursor.execute(
        "UPDATE racoon_jobs SET processed = False WHERE jobid = %s",
        (row["jobid"],),
    )
    mcursor.close()
    pgconn.commit()


def check_for_work():
    """See if we have any requests to process!"""
    pgconn = get_dbconn("mesosite")
    mcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    mcursor2 = pgconn.cursor()
    mcursor.execute(
        "SELECT jobid, wfo, radar, sts at time zone 'UTC' as sts, "
        "ets at time zone 'UTC' as ets, nexrad_product, wtype "
        "from racoon_jobs WHERE processed = False"
    )
    jobs = []
    for row in mcursor:
        jobs.append(row)
        mcursor2.execute(
            "UPDATE racoon_jobs SET processed = True WHERE jobid = %s",
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
    pgconn = get_dbconn("postgis")
    pcursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = f"""
    WITH stormbased as (
        SELECT phenomena, eventid, issue, expire,
        ST_Area(ST_Transform(geom,2163))/1000000.0 as polyarea
        from sbw_{sts:%Y} WHERE issue BETWEEN
        '{sts:%Y-%m-%d %H:%M}+00' and '{ets:%Y-%m-%d %H:%M}+00' and
        wfo = '{wfo}' and phenomena in {phenomenas} and significance = 'W'
        and status = 'NEW'
    ), countybased as (
        SELECT phenomena, eventid,
        sum(ST_Area(ST_Transform(u.geom,2163))/1000000.0) as countyarea
        from warnings_{sts:%Y} w JOIN ugcs u on (u.gid = w.gid) WHERE
        issue BETWEEN '{sts:%Y-%m-%d %H:%M}+00' and
        '{ets:%Y-%m-%d %H:%M}+00' and
        w.wfo = '{wfo}' and phenomena in {phenomenas} and significance = 'W'
        GROUP by phenomena, eventid
    )

    SELECT s.phenomena, s.eventid,
    s.issue at time zone 'UTC' as issue,
    s.expire at time zone 'UTC' as expire, s.polyarea,
    c.countyarea from stormbased s JOIN countybased c
    on (c.eventid = s.eventid and c.phenomena = s.phenomena)
    """
    pcursor.execute(sql)
    res = []
    for row in pcursor:
        res.append(row)
    pgconn.close()
    return res


def do_job(job):
    """Do something"""
    warnings = get_warnings(job["sts"], job["ets"], job["wfo"], job["wtype"])

    mydir = os.path.join(TMPDIR, f"{job['jobid']}")
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    os.chdir(mydir)

    basefn = (
        f"{job['wfo']}-{job['wtype'].replace(',', '_')}-{job['radar']}-"
        f"{job['sts']:%Y%m%d%H}-{job['ets']:%Y%m%d%H}"
    )
    outputfile = f"{basefn}.odp"

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
    textbox.addElement(P(text=f"WFO: {job['wfo']}"))
    textbox.addElement(
        P(text=f"Radar: {job['radar']} Product: {job['nexrad_product']}")
    )
    textbox.addElement(P(text=f"Phenomenas: {job['wtype']}"))
    textbox.addElement(P(text=f"Start Time: {job['sts']:%d %b %Y %H} UTC"))
    textbox.addElement(P(text=f"End Time: {job['ets']:%d %b %Y %H} UTC"))
    textbox.addElement(P(text=""))
    textbox.addElement(P(text=f"Raccoon Version: {__REV__}"))
    textbox.addElement(P(text=f"Generated on: {utc():%d %b %Y %H:%M %Z}"))
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
                text=(
                    f"{job['sts']:%Y}.O.NEW.K{job['wfo']}."
                    f"{warning['phenomena']}.W.{warning['eventid']:04.0f}"
                )
            )
        )
        textbox.addElement(
            P(text=f"Issue: {warning['issue']:%d %b %Y %H:%M} UTC")
        )
        textbox.addElement(
            P(text=f"Expire: {warning['expire']:%d %b %Y %H:%M} UTC")
        )
        zz = warning["polyarea"] / warning["countyarea"] * 100.0
        textbox.addElement(
            P(
                text=(
                    f"Poly Area: {warning['polyarea']:.1f} sq km "
                    f"({(warning['polyarea'] * 0.386102):.1f} sq mi) "
                    f"[{zz:.1f}% vs County]"
                )
            )
        )
        zz = warning["countyarea"] * 0.386102
        textbox.addElement(
            P(
                text=(
                    f"County Area: {warning['countyarea']:.1f} "
                    f"square km ({zz:.1f} square miles)"
                )
            )
        )

        url = (
            "http://iem.local/GIS/radmap.php?"
            "layers[]=places&layers[]=legend&layers[]=ci&layers[]=cbw"
            "&layers[]=sbw&layers[]=uscounties&layers[]=bufferedlsr"
            f"&lsrbuffer=15&vtec={job['sts']:%Y}.O.NEW.K{job['wfo']}."
            f"{warning['phenomena']}.W.{warning['eventid']:04.0f}"
        )

        cmd = f"wget -q -O {i}.png '{url}'"
        os.system(cmd)
        photoframe = Frame(
            stylename=photostyle,
            width="480pt",
            height="360pt",
            x="160pt",
            y="200pt",
        )
        page.addElement(photoframe)
        href = doc.addPicture(f"{i}.png")
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
                    text=(
                        f"{warning['phenomena']}.W.{warning['eventid']:04.0f} "
                        f"Time: {now:%d %b %Y %H%M} UTC"
                    )
                )
            )

            if job["nexrad_product"] == "N0U":
                if now < SUPER_RES:
                    n0qn0r = "N0V"
                elif now < N0B_SWITCH:
                    n0qn0r = "N0U"
                else:
                    n0qn0r = "N0S"
            else:
                if now < SUPER_RES:
                    n0qn0r = "N0R"
                elif now < N0B_SWITCH:
                    n0qn0r = "N0Q"
                else:
                    n0qn0r = "N0B"
            zz = now + datetime.timedelta(minutes=15)
            url = (
                "http://iem.local/GIS/radmap.php?layers[]=ridge&"
                f"ridge_product={n0qn0r}&ridge_radar={job['radar']}&"
                "layers[]=sbw&layers[]=sbwh&layers[]=uscounties&"
                f"layers[]=lsrs&ts2={zz:%Y%m%d%H%M}&vtec="
                f"{job['sts']:%Y}.O.NEW.K{job['wfo']}.{warning['phenomena']}."
                f"W.{warning['eventid']:04.0f}&ts={now:%Y%m%d%H%M}"
            )

            cmd = f"wget -q -O {i}.png '{url}'"
            os.system(cmd)
            photoframe = Frame(
                stylename=photostyle,
                width="640pt",
                height="480pt",
                x="80pt",
                y="70pt",
            )
            page.addElement(photoframe)
            href = doc.addPicture(f"{i}.png")
            photoframe.addElement(Image(href=href))
            i += 1

    doc.save(outputfile)
    del doc
    subprocess.call(["unoconv", "-f", "ppt", outputfile])
    pptfn = f"{basefn}.ppt"
    LOG.warning("Generated %s with %s slides", pptfn, i)
    if os.path.isfile(pptfn):
        LOG.warning("...copied to webfolder")
        shutil.copyfile(pptfn, f"/mesonet/share/pickup/raccoon/{pptfn}")
        # Cleanup
        os.chdir(TMPDIR)
        subprocess.call(["rm", "-rf", f"{job['jobid']}"])
    else:
        LOG.warning("Uh oh, no output file, lets kill soffice.bin")
        subprocess.call(["pkill", "--signal", "9", "soffice.bin"])
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
