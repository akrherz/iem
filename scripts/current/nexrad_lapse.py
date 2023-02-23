"""Create a pretty aGIF."""
import datetime
import os
import subprocess
import tempfile

import pytz
from PIL import Image, ImageDraw, ImageFont
from pyiem.plot import MapPlot
from pyiem.util import logger, utc

LOG = logger()
TMPDIR = "/tmp/nexrad_lapse"


def setupdir():
    """Get us in the empire state of mind."""
    if not os.path.isdir(TMPDIR):
        os.makedirs(TMPDIR)
    # Cleanup
    os.chdir(TMPDIR)
    subprocess.call("tmpwatch 24 .", shell=True)


def run(sts, ets):
    """Run between start and end."""
    interval = datetime.timedelta(minutes=5)
    now = sts
    while now <= ets:
        fn = now.strftime("frame_%Y%m%d%H%M.png")
        if not os.path.isfile(fn):
            LOG.info("Creating %s", fn)
            mp = MapPlot(
                twitter=True,
                title="NWS NEXRAD Mosaic",
            )
            mp.overlay_nexrad(now)
            mp.drawcounties()
            mp.fig.savefig(fn)
            mp.close()
        now += interval

    now = sts
    tmpfn = tempfile.NamedTemporaryFile()
    tmpname = tmpfn.name.split("/")[-1]
    tmpfn.close()
    images = []
    total_seconds = (ets - sts).total_seconds()
    font_path = "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf"
    font = ImageFont.truetype(font_path, size=16)
    while now <= ets:
        framefn = now.strftime("frame_%Y%m%d%H%M.png")
        LOG.info("Processing %s", framefn)
        im = Image.open(framefn)
        draw = ImageDraw.Draw(im)
        draw.rectangle(
            [110, 60, 450, 45], fill="#FFFFFF", outline="#000000", width=3
        )
        ratio = (now - sts).total_seconds() / total_seconds
        draw.rectangle(
            [110 + 340 * ratio, 58, 450, 47],
            fill="#000000",
            outline="#000000",
            width=3,
        )
        text = now.astimezone(pytz.timezone("America/Chicago")).strftime(
            "%A %-2I:%M %p"
        )
        draw.text((456, 47), text, fill="#000000", font=font)
        images.append(im)
        now += interval

    # Make the GIF
    LOG.info("Creating aPNG %s.png", tmpname)
    durations = [100] * len(images)
    durations[-1] = 2000
    images[0].save(
        f"{tmpname}.png",
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        format="PNG",
    )

    subprocess.call(
        [
            "pqinsert",
            "-i",
            "-p",
            (
                f"data c {ets.strftime('%Y%m%d%H%M')} lapse/iowa_nexrad.png "
                "lapse/iowa_nexrad.png"
            ),
            tmpname,
            f"{tmpname}.png",
        ]
    )
    os.unlink(f"{tmpname}.png")


def main():
    """Go Main Go."""
    # ets is something now modulo 5
    ets = utc()
    ets -= datetime.timedelta(minutes=ets.minute % 5)
    sts = ets - datetime.timedelta(hours=2)
    LOG.info("running for %s to %s", sts, ets)
    setupdir()
    run(sts, ets)


if __name__ == "__main__":
    main()
