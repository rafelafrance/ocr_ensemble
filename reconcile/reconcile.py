#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
import textwrap
from collections import defaultdict
from pathlib import Path
from pprint import pp
from typing import Any

import traiter.pylib.darwin_core as t_dwc
from pylib import log
from traiter.pylib import util as t_util
from traiter.pylib.reconcilers.base import TEMPLATE
from traiter.pylib.reconcilers.date_ import Date
from traiter.pylib.reconcilers.elevation import Elevation
from traiter.pylib.reconcilers.habitat import Habitat
from traiter.pylib.reconcilers.lat_long import LatLong


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
        count_keys(args.openai_dir, openai_stems)

    else:
        build_template()

        for stem in stems:
            text = get_text(args.text_dir, stem)
            rule_traits = get_rule_traits(args.traiter_dir, stem)
            openai_traits = get_openai_traits(args.openai_dir, stem)

            traits, errors = get_traits(text, stem, rule_traits, openai_traits)
            if errors > args.errors:
                logging.error(f"Total errors: {errors}")
                sys.exit(1)

            save_traits(args.formatted_dir, stem, traits)

    log.finished()


def build_template():
    Date()
    Elevation()
    Habitat()
    LatLong()


def get_traits(text, stem, r_traits, o_traits) -> tuple[dict[str, Any], int]:
    print("=" * 80)
    print(stem)
    print()
    print(text)
    print()
    pp(r_traits)
    print()
    pp(o_traits)
    print()

    traits = {}
    errors = 0

    for func in TEMPLATE.reconcile:
        try:
            traits |= func(r_traits, o_traits)
        except ValueError as err:
            logging.error(f"{err} [{stem}]")
            errors += 1

    print()
    pp(traits)
    print()

    skipped = sorted(set(o_traits.keys()) - set(traits.keys()))
    logging.info(f"Missed keys {', '.join(skipped)}")
    print()
    valid = [k for k in skipped if k in t_dwc.CORE]
    logging.info(f"Missed valid keys {', '.join(valid)}")
    print()

    return traits, errors


def get_text(text_dir, stem) -> str:
    path = text_dir / f"{stem}.txt"
    with open(path) as f:
        text = f.read()
    text = t_util.compress(text)
    return text


def get_rule_traits(traiter_dir, stem) -> dict[str, Any]:
    path = traiter_dir / f"{stem}.json"
    with open(path) as f:
        traiter = json.load(f)
    return traiter


def get_openai_traits(openai_dir, stem) -> dict[str, Any]:
    path = openai_dir / f"{stem}.json"
    with open(path) as f:
        openai = json.load(f)

    new = {}
    for key, value in openai.items():
        new[key] = value
        if isinstance(value, dict):
            new |= {k: v for k, v in value.items()}

    new = {clean_key(k): v for k, v in new.items()}
    return new


def save_traits(parsed_dir, stem, traits):
    path = parsed_dir / f"{stem}.json"
    with open(path, "w") as f:
        json.dump(traits, f)


def clean_key(key) -> str:
    key = key.removeprefix("dc:").removeprefix("dcterms:").removeprefix("dnz:")
    key = key.removeprefix("dwc-").removeprefix("dwc:").removeprefix("dwc")
    key = key.removeprefix("Dc:").removeprefix("DwC:")
    key = key.strip(":")
    key = key.strip()

    if len(key) > 2:
        key = key[0].lower() + key[1:]

    key = t_dwc.DarwinCore.ns(key)
    return key


def count_keys(dir_, stems) -> dict[str, int]:
    keys = defaultdict(int)

    for stem in stems:
        path = dir_ / f"{stem}.json"
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

    logging.info(f"{valid_count}/{len(keys)} valid keys")
    logging.info(f"{len(keys) - valid_count}/{len(keys)} invalid keys")

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
        "--errors",
        metavar="INT",
        type=int,
        default=999_999_999,
        help="""Allow this many errors before exiting.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
