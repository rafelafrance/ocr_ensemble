import csv
from pathlib import Path

DWC = "dwc:"
DC = "dc:"

SEP = " | "
FIELD_SEP = " ~ "


def read_dwc_terms():
    core, dublin = {}, {}

    path = Path(__file__).parent / "dwc_terms.csv"
    with open(path) as f:
        for row in csv.DictReader(f):
            name = row["term_localName"]
            name = name[0].lower() + name[1:]

            if row["iri"].find("dublincore") > -1:
                name = DC + name
                dublin[name] = row

            else:
                name = DWC + name

            core[name] = row

    return core, dublin


CORE, DUBLIN = read_dwc_terms()


def ns(name):
    namespace = DC if name in DUBLIN else DWC
    return name if name.startswith(namespace) else namespace + name
