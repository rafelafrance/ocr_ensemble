#!/usr/bin/env python3
import argparse
import json
import logging
import os
import textwrap
from collections import defaultdict
from pathlib import Path
from pprint import pp
from typing import Any

import traiter.pylib.darwin_core as t_dwc
from flora.pylib import pipeline
from pylib import log
from tqdm import tqdm
from traiter.pylib import util as t_util


def main():
    log.started()
    args = parse_args()

    nlp = pipeline.build()

    text_stems = set(p.stem for p in args.text_dir.glob("*"))
    openai_stems = set(p.stem for p in args.openai_dir.glob("*"))

    os.makedirs(args.parsed_dir, exist_ok=True)

    stems = sorted(text_stems & openai_stems)

    logging.info(
        f"Text: {len(text_stems)}, "
        f"OpenAI: {len(openai_stems)}, "
        f"Intersection: {len(stems)}, "
        f"All numbers the same: {len(text_stems) == len(openai_stems) == len(stems)}."
    )

    for i, stem in tqdm(enumerate(stems)):
        text = get_text(args.text_dir, stem)
        rule_traits = get_rule_traits(text, nlp)
        openai_traits = get_openai_traits(args.openai_dir, stem)

        traits = validate_traits(text, stem, rule_traits, openai_traits)

        save_traits(args.parsed_dir, stem, traits)

        if i == 1:
            break

    log.finished()


def validate_traits(text, stem, r_traits, o_traits) -> dict[str, Any]:
    print("=" * 80)
    print(text)
    print()
    pp(r_traits)
    print()
    pp(o_traits)
    print()

    traits = {}
    o_core = {k: v for k, v in o_traits.items() if k.casefold().find("dynamic") == -1}

    for key, o_val in o_core.items():
        if key in r_traits and o_traits[key] == r_traits[key]:
            traits[key] = o_val

        elif key in r_traits and o_traits[key] != r_traits[key]:
            logging.error(f"MISMATCH {key}: {o_val} != {r_traits[key]}, in {stem}")

        else:
            logging.error(f"{key}: = {o_val}, in {stem}")

    return traits


def get_text(text_dir, stem) -> str:
    path = text_dir / f"{stem}.txt"
    with open(path) as f:
        text = f.read()
    text = t_util.compress(text)
    return text


def get_rule_traits(text, nlp) -> dict[str, Any]:
    doc = nlp(text)

    traits = defaultdict(list)

    for e in doc.ents:
        dwc = t_dwc.DarwinCore()
        trait = e._.trait.to_dwc(dwc).to_dict()
        core = {k: v for k, v in trait.items() if k != t_dwc.DYN}
        for key, value in core.items():
            traits[key].append(value)

    traits = {k: t_dwc.DarwinCore.convert_value_list(k, v) for k, v in traits.items()}

    return traits


def get_openai_traits(openai_dir, stem) -> dict[str, Any]:
    path = openai_dir / f"{stem}.json"
    with open(path) as f:
        openai = json.load(f)
    openai = {t_dwc.DarwinCore.ns(k): v for k, v in openai.items()}
    return openai


def save_traits(parsed_dir, stem, traits):
    path = parsed_dir / f"{stem}.json"
    with open(path, "w") as f:
        json.dump(traits, f)


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
        help="""Directory containing the OCR result files.""",
    )

    arg_parser.add_argument(
        "--openai-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Directory holding cleaned openai output.""",
    )

    arg_parser.add_argument(
        "--parsed-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Put the parsed result files into this directory.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
