"""Sucks that the raw data is only found in the PDFs.

Run from TBD
"""
import datetime
import os
import tempfile
import warnings

import click
import httpx
import pytesseract
from pdf2image import convert_from_path
from pyiem.database import get_dbconnc
from pyiem.util import logger

# emitted whilst parsing the PDF
warnings.simplefilter("ignore", UserWarning)
BASEURL = (
    "https://www.nass.usda.gov/Statistics_by_State/Iowa/Publications/"
    "Crop_Progress_&_Condition/"
)
REMAPED = {
    "hay, alfalfa, first cutting": "hay, alfalfa, 1st cutting",
    "alfalfa hay first cutting": "hay, alfalfa, 1st cutting",
    "alfalfa hay, first cutting": "hay, alfalfa, 1st cutting",
    "hay, alfalfa, second cutting": "hay, alfalfa, 2nd cutting",
    "alfalfa hay second cutting": "hay, alfalfa, 2nd cutting",
    "alfalfa hay, second cutting": "hay, alfalfa, 2nd cutting",
    "hay, alfalfa, third cutting": "hay, alfalfa, 3rd cutting",
    "alfalfa hay third cutting": "hay, alfalfa, 3rd cutting",
    "alfalfa hay, third cutting": "hay, alfalfa, 3rd cutting",
    "oats harvested": "oats harvested for grain",
}
DOMAIN = [
    "corn dented",
    "corn dough",
    "corn emerged",
    "corn mature",
    "corn planted",
    "corn harvested for grain",
    "corn silking",
    "days suitable",
    "hay, alfalfa, 1st cutting",
    "hay, alfalfa, 2nd cutting",
    "hay, alfalfa, 3rd cutting",
    "oats coloring",
    "oats emerged",
    "oats harvested for grain",
    "oats headed",
    "oats planted",
    "soybeans blooming",
    "soybeans coloring",
    "soybeans dropping leaves",
    "soybeans planted",
    "soybeans emerged",
    "soybeans setting pods",
    "subsoil moisture very short",
    "subsoil moisture short",
    "subsoil moisture adequate",
    "subsoil moisture surplus",
    "topsoil moisture very short",
    "topsoil moisture short",
    "topsoil moisture adequate",
    "topsoil moisture surplus",
]
LOG = logger()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def process_lines(valid, lines) -> int:
    """Process a table."""
    # Quacks like a duck here
    prefix = ""
    inserts = 0
    for line in lines:
        line = (
            line.strip()
            .lower()
            .replace("a1", "11")
            .replace("ii", "11")
            .replace("g1", "91")
            .replace("plante:", "planted")
            .replace("0c cece", "")
        )
        if line in ["topsoil moisture", "subsoil moisture"]:
            prefix = line + " "
            continue
        # A good data line has some alpha label followed by 10+ numbers
        tokens = line.split()
        if len(tokens) < 10:
            continue
        # A first guess
        if not is_number(tokens[-10]) or not is_number(tokens[-9]):
            continue
        label = prefix
        numbers = []
        for i, token in enumerate(tokens):
            if is_number(token):
                numbers = tokens[i:]
                break
            label += token.replace(".", "") + " "
        label = label.strip()
        label = REMAPED.get(label, label)
        if label not in DOMAIN:
            # Attempt to fix OCR errors
            for domain in DOMAIN:
                if label.startswith(domain):
                    label = domain
                    break
        if label not in DOMAIN:
            LOG.info("Unknown label: |%s| line: %s", label, line)
            continue
        ingest(valid, label, numbers)
        inserts += 1
    return inserts


def ingest(valid, label, numbers):
    """We have content."""
    # Some QC
    if label == "days suitable":
        numbers = [float(x) for x in numbers[:10]]
        for i in range(0, 10):
            if numbers[i] >= 10:
                numbers[i] = numbers[i] / 10.0  # OCR Fail
    # OCR Fail
    for i in range(0, 10):
        if numbers[i] in ["(", ")"]:
            numbers[i] = 0
    LOG.info("Ingesting %s %s", label, numbers[:10])
    conn, cursor = get_dbconnc("coop")
    cursor.execute(
        "delete from nass_iowa where valid = %s and metric = %s",
        (valid, label),
    )
    cursor.execute(
        "INSERT into nass_iowa(valid, metric, nw, nc, ne, wc, c, ec, "
        "sw, sc, se, iowa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s)",
        (valid, label, *numbers[:10]),
    )
    cursor.close()
    conn.commit()
    conn.close()


def get_url(valid):
    """Le Sigh."""
    uri = (
        f"{BASEURL}{valid:%Y}/IA-Crop-Progress-"
        f"{valid:%m}-{valid:%d}-{valid:%y}.pdf"
    )
    if valid.year <= 2017:
        uri = uri.replace("-", "_")
    if valid.year <= 2016:
        uri = uri.replace("_Crop_Progress", "")
    return uri


def workflow(sunday):
    """Do Work."""
    # Find the PDF by looking at Monday, Tuesday, and Wednesday
    found = False
    for day in [1, 2, 3, 0]:
        valid = sunday + datetime.timedelta(days=day)
        uri = get_url(valid)
        LOG.info("Attempting %s", uri)
        req = httpx.get(uri)
        if req.status_code == 200:
            found = True
            break
    if not found:
        LOG.info("Failed to find PDF for %s", sunday)
        return
    with tempfile.NamedTemporaryFile("wb", delete=False) as fh:
        fh.write(req.content)
    pdffn = fh.name + ".pdf"
    os.rename(fh.name, pdffn)
    pages = convert_from_path(pdffn, 200, first_page=1, last_page=1)
    extracted_text = ""
    # Loop through each image and extract the text
    for page in pages:
        extracted_text += pytesseract.image_to_string(page)
    process_lines(sunday, extracted_text.split("\n"))
    os.unlink(pdffn)


@click.command()
@click.option("--sunday", help="NASS Analysis Date", type=click.DateTime())
@click.option("--weeks", help="Number of weeks to run", type=int, default=1)
def main(sunday, weeks):
    """Go Main Go."""
    for i in range(weeks):
        workflow(sunday)
        sunday += datetime.timedelta(days=7)


if __name__ == "__main__":
    main()
