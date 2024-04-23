"""Sucks that the raw data is only found in the PDFs.

Run from RUN_12Z.sh on Tuesdays
"""

import datetime
import os
import tempfile
import warnings

import click
import httpx
import pytesseract
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
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
    "alfalfa hay, first cuttin": "hay, alfalfa, 1st cutting",
    "alfalfa hay, first cutting": "hay, alfalfa, 1st cutting",
    "hay, alfalfa - first crop harvested": "hay, alfalfa, 1st cutting",
    "hay, alfalfa - 1st cutting": "hay, alfalfa, 1st cutting",
    "hay, alfalfa, second cutting": "hay, alfalfa, 2nd cutting",
    "alfalfa hay second cutting": "hay, alfalfa, 2nd cutting",
    "alfalfa hay, second cutting": "hay, alfalfa, 2nd cutting",
    "hay, alfalfa, third cutting": "hay, alfalfa, 3rd cutting",
    "alfalfa hay third cutting": "hay, alfalfa, 3rd cutting",
    "alfalfa hay, third cutting": "hay, alfalfa, 3rd cutting",
    "oats harvested": "oats harvested for grain",
    "oats emerge": "oats emerged",
    "oats emerget": "oats emerged",
    "cor planted": "corn planted",
    "subsoil moisture adequat": "subsoil moisture adequate",
    "ubsoil moisture": "subsoil moisture",
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
    "fertilizer application completed",
    "hay, alfalfa, 1st cutting",
    "hay, alfalfa, 2nd cutting",
    "hay, alfalfa, 3rd cutting",
    "oats coloring",
    "oats emerged",
    "oats harvested for grain",
    "oats headed",
    "oats planted",
    "oats turning color",
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


def glean_labels(label) -> list:
    """Figure out what we have here."""
    res = []
    prefix = ""
    for token in [x.strip().lower() for x in label.split("\n")]:
        token = token.replace(".", "").strip()
        token = REMAPED.get(token, token)
        if token.find("moisture") > -1:
            prefix = f"{token} "
            continue
        token = f"{prefix}{token}"
        if token in DOMAIN:
            res.append(token)
    return res


def process_lines_pdfminer(valid, lines) -> int:
    """Special magic here."""
    labels = ""
    numbers = []
    for line in lines:
        line = line.strip().lower()
        if line in [""]:
            continue
        if line in ["topsoil moisture", "subsoil moisture"]:
            labels += line + "\n"
            continue
        if line.find("...") > -1:
            labels += line.replace(".", "") + "\n"
            continue
        if labels != "":
            if is_number(line):
                numbers.append(line)
                continue
            metrics = glean_labels(labels)
            if metrics and len(numbers) > (len(metrics) * 10):
                for i, metric in enumerate(metrics):
                    nums = [numbers[j * len(metrics) + i] for j in range(10)]
                    ingest(valid, metric, nums)
            labels = ""
            numbers = []


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
            .replace("00.c ceed", "")
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
    if numbers[1] == "|":
        numbers.pop(1)
    numbers = [
        x.replace("]", "")
        .replace("l", "1")
        .replace("|", "")
        .replace(")", "")
        .replace("}", "")
        .replace(",", "")
        .replace("5a", "54")
        .replace("a", "")
        for x in numbers
    ]
    if label == "days suitable":
        numbers = [float(x) for x in numbers[:10]]
        for i in range(10):
            if numbers[i] >= 10:
                numbers[i] = numbers[i] / 10.0  # OCR Fail
    # OCR Fail
    for i in range(10):
        if numbers[i] in ["(", ")", ""]:
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
    if datetime.datetime(2013, 6, 1) < valid < datetime.datetime(2014, 1, 1):
        uri = uri.replace("_Crop_Progress_", "")
    elif valid.year <= 2016:
        uri = uri.replace("_Crop_Progress", "")
    if datetime.datetime(2014, 5, 20) < valid < datetime.datetime(2014, 6, 29):
        uri = uri.replace("_14", "__14")
    return uri


def workflow(sunday, engine, remotefn):
    """Do Work."""
    # Find the PDF by looking at Monday, Tuesday, and Wednesday
    found = False
    if remotefn is not None:
        req = httpx.get(f"{BASEURL}/{sunday:%Y}/{remotefn}")
    else:
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
    if engine == "pdfminer":
        extracted_text = extract_text(pdffn, maxpages=1)
        process_lines_pdfminer(sunday, extracted_text.split("\n"))
    else:
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
@click.option("--engine", help="PDF Engine", default="pytesseract")
@click.option("--remotefn", help="Remote Filename", default=None)
def main(sunday, weeks, engine, remotefn):
    """Go Main Go."""
    for _ in range(weeks):
        workflow(sunday, engine, remotefn)
        sunday += datetime.timedelta(days=7)


if __name__ == "__main__":
    main()
