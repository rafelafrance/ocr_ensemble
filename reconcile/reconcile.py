#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from pprint import pp
from typing import Any

import traiter.pylib.darwin_core as t_dwc
from flora.pylib.reconcilers.admin_unit import AdminUnit
from flora.pylib.reconcilers.id_number import IdNumber
from flora.pylib.reconcilers.job import Job
from flora.pylib.reconcilers.locality import Locality
from flora.pylib.reconcilers.record_number import RecordNumber
from flora.pylib.reconcilers.sex import Sex
from flora.pylib.reconcilers.taxon_assoc import TaxonAssociation
from flora.pylib.reconcilers.taxon_auth import TaxonAuthority
from flora.pylib.reconcilers.taxon_name import TaxonName
from flora.pylib.reconcilers.taxon_rank import TaxonRank
from pylib import log
from traiter.pylib import util as t_util
from traiter.pylib.reconcilers.base import Template
from traiter.pylib.reconcilers.coordinate_precision import CoordinatePrecision
from traiter.pylib.reconcilers.coordinate_uncertainty import CoordinateUncertainty
from traiter.pylib.reconcilers.decimal_latitude import DecimalLatitude
from traiter.pylib.reconcilers.decimal_longitude import DecimalLongitude
from traiter.pylib.reconcilers.event_date import EventDate
from traiter.pylib.reconcilers.geodetic_datum import GeodeticDatum
from traiter.pylib.reconcilers.habitat import Habitat
from traiter.pylib.reconcilers.maximum_elevation import MaximumElevationInMeters
from traiter.pylib.reconcilers.minimum_elevation import MinimumElevationInMeters
from traiter.pylib.reconcilers.verbatim_coordinates import VerbatimCoordinates
from traiter.pylib.reconcilers.verbatim_elevation import VerbatimElevation
from traiter.pylib.reconcilers.verbatim_system import VerbatimCoordinateSystem


@dataclass
class Row:
    stem: str
    text: str = ""
    traiter: dict[str, Any] = field(default_factory=dict)
    openai: dict[str, Any] = field(default_factory=dict)
    reconciled: dict[str, Any] = field(default_factory=dict)
    missed: set[str] = field(default_factory=set)
    errors: list[str] = field(default_factory=list)

    def get_text(self, text_dir):
        path = text_dir / f"{self.stem}.txt"
        with open(path) as f:
            text = f.read()
        self.text = t_util.compress(text)

    def get_traiter(self, traiter_dir):
        path = traiter_dir / f"{self.stem}.json"
        with open(path) as f:
            self.traiter = json.load(f)

    def get_openai(self, openai_dir):
        path = openai_dir / f"{self.stem}.json"
        with open(path) as f:
            openai = json.load(f)

        new = {}
        for key, value in openai.items():
            new[key] = value
            if isinstance(value, dict):
                new |= {k: v for k, v in value.items()}

        self.openai = {clean_key(k): v for k, v in new.items()}

    def reconcile(self, template):
        for func in template.actions:
            try:
                self.reconciled |= func(self.traiter, self.openai)
            except ValueError as err:
                self.errors.append(str(err))

        self.missed = set(self.openai.keys()) - set(self.reconciled.keys())

    def save_traits(self, parsed_dir):
        path = parsed_dir / f"{self.stem}.json"
        with open(path, "w") as f:
            json.dump(self.reconciled, f, indent=4)

    def verbose_start(self):
        print("=" * 80)
        print(self.stem)
        print()

    def verbose(self):
        if self.errors:
            print()
        print(f"Errors: {self.errors}")
        print()
        print("---- Text ", "-" * 40)
        print(self.text)
        print()
        print("---- Traiter ", "-" * 40)
        pp(self.traiter)
        print()
        print("---- OpenAI ", "-" * 40)
        pp(self.openai)
        print()
        print("---- Reconciled ", "-" * 40)
        pp(self.reconciled)
        print()


def main():
    log.started()
    args = parse_args()

    text_stems = set(p.stem for p in args.text_dir.glob("*"))
    traiter_stems = set(p.stem for p in args.traiter_dir.glob("*"))
    openai_stems = set(p.stem for p in args.openai_dir.glob("*"))

    os.makedirs(args.formatted_dir, exist_ok=True)

    stems = sorted(text_stems & openai_stems & traiter_stems)

    logging.info(
        f"Text: {len(text_stems)}, "
        f"Traiter: {len(traiter_stems)}, "
        f"OpenAI: {len(openai_stems)}, "
        f"Intersection: {len(stems)}, "
        f"All numbers the same: "
        f"{len(text_stems) == len(openai_stems) == len(stems) == len(traiter_stems)}."
    )

    if args.count:
        count_keys(args.openai_dir)

    else:
        template = Template(
            EventDate,
            MinimumElevationInMeters,
            MaximumElevationInMeters,
            VerbatimElevation,
            Habitat,
            DecimalLatitude,
            DecimalLongitude,
            CoordinateUncertainty,
            CoordinatePrecision,
            GeodeticDatum,
            VerbatimCoordinateSystem,
            VerbatimCoordinates,
            AdminUnit,
            IdNumber,
            RecordNumber,
            Locality,
            Sex,
            Job,
            TaxonAssociation,
            TaxonAuthority,
            TaxonName,
            TaxonRank,
        )

        total_errors = 0
        rows = []

        for stem in stems:
            row = Row(stem=stem)
            rows.append(row)

            row.get_text(args.text_dir)
            row.get_traiter(args.traiter_dir)
            row.get_openai(args.openai_dir)

            if args.verbose:
                row.verbose_start()

            row.reconcile(template)

            row.save_traits(args.formatted_dir)

            if args.verbose:
                row.verbose()

            total_errors += len(row.errors)
            if total_errors > args.max_errors:
                logging.error(f"Max errors of {args.max_errors} exceeded")
                sys.exit(1)

        if args.verbose > 1:
            show_missed(rows)

        logging.info(f"Total errors: {total_errors}")
    log.finished()


def clean_key(key) -> str:
    key = key.removeprefix("dcterms:").removeprefix("dnz:").removeprefix("DwC:")
    key = key.removeprefix("dwc:").removeprefix("dwc").removeprefix("dwc-")
    key = key.removeprefix("dc:").removeprefix("Dc:")
    key = key.strip(":")
    key = key.strip()

    if len(key) > 2:
        key = key[0].lower() + key[1:]

    key = t_dwc.DarwinCore.ns(key)
    return key


def show_missed(rows):
    missed = defaultdict(int)
    for row in rows:
        for m in row.missed:
            missed[m] += 1

    missed = dict(sorted(missed.items()))
    print("---- Missed Keys ", "-" * 40)
    pp(missed)
    print()

    valid = {k: v for k, v in missed.items() if k in t_dwc.CORE}
    print("---- Missed DwC Keys ", "-" * 40)
    pp(valid)
    print()


def count_keys(dir_) -> dict[str, int]:
    keys = defaultdict(int)

    for path in dir_.glob("*.json"):
        with open(path) as f:
            obj = json.load(f)

        for key in obj.keys():
            key = clean_key(key)
            keys[key] += 1

    keys = dict(sorted(keys.items()))

    valid_count = 0
    print("key,valid,count")
    for key, count in keys.items():
        valid = 1 if key in t_dwc.CORE else ""
        print(f"{key},{valid},{count}")
        valid_count += 1 if valid else 0

    print(f"{valid_count}/{len(keys)} valid keys")
    print(f"{len(keys) - valid_count}/{len(keys)} invalid keys")

    return keys


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent("""Format and validate ChatGPT results."""),
    )

    arg_parser.add_argument(
        "--text-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get OCR text output files from this directory.""",
    )

    arg_parser.add_argument(
        "--openai-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get OpenAI JSON files from this directory.""",
    )

    arg_parser.add_argument(
        "--traiter-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get traiter JSON files from this directory.""",
    )

    arg_parser.add_argument(
        "--formatted-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Put the formatted result files into this directory.""",
    )

    arg_parser.add_argument(
        "--count",
        action="store_true",
        help="""Count the keys in the openAI output.""",
    )

    arg_parser.add_argument(
        "--max-errors",
        "-e",
        metavar="INT",
        type=int,
        default=999_999_999,
        help="""Allow this many errors before exiting.""",
    )

    arg_parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="""Print information for debugging.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
