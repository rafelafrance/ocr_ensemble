#!/usr/bin/env python3
import argparse
import csv
import random
import textwrap
from pathlib import Path

from pylib import log


def main():
    log.started()
    args = parse_args()

    random.seed(args.seed)

    text_paths = set(p.stem for p in args.text_dir.glob("*"))
    openai_paths = set(p.stem for p in args.openai_dir.glob("*"))
    traiter_paths = set(p.stem for p in args.traiter_dir.glob("*"))

    paths = sorted(text_paths & openai_paths & traiter_paths)

    sample = random.sample(paths, args.sample)

    with open(args.csv_file, "w") as out:
        writer = csv.writer(out)
        writer.writerow(["ocr_text", "gpt4_output", "traiter_output"])

        for stem in sample:
            path = args.text_dir / f"{stem}.txt"
            with open(path) as f:
                text = f.read()

            path = args.openai_dir / f"{stem}.json"
            with open(path) as f:
                openai = f.read()

            path = args.traiter_dir / f"{stem}.json"
            with open(path) as f:
                traiter = f.read()

            writer.writerow([text, openai, traiter])

    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """Look for confabulations in ChatGPT trait extractions."""
        ),
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
        help="""Directory holding the openai output.""",
    )

    arg_parser.add_argument(
        "--traiter-dir",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Get traiter JSON files from this directory.""",
    )

    arg_parser.add_argument(
        "--csv-file",
        metavar="PATH",
        type=Path,
        required=True,
        help="""Output the data to this CSV file.""",
    )

    arg_parser.add_argument(
        "--sample",
        metavar="PATH",
        type=int,
        default=200,
        help="""Number of paths to sample.""",
    )

    arg_parser.add_argument(
        "--seed",
        metavar="PATH",
        type=int,
        default=4438,
        help="""Random number seed.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
