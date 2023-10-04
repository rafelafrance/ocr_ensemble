#!/usr/bin/env python3
"""Build an expedition to determine the quality of OCR output."""
import argparse
import textwrap
from pathlib import Path

from pylib.ocr.is_correction_needed import build_expedition
from traiter.pylib import log


def main():
    log.started()
    args = parse_args()
    if args.side_by_side:
        build_expedition.build_side_by_side(args)
    else:
        build_expedition.build_2_files(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    description = """Build the 'Is Correction Needed?' expedition"""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--database",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Path to a digi-leap database.""",
    )

    arg_parser.add_argument(
        "--expedition-dir",
        required=True,
        type=Path,
        metavar="PATH",
        help="""Place expedition files in this directory.""",
    )

    arg_parser.add_argument(
        "--ocr-set",
        required=True,
        metavar="NAME",
        help="""Use this OCR output.""",
    )

    arg_parser.add_argument(
        "--side-by-side",
        action="store_true",
        help="Change the output to save the output as one file with image and text.",
    )

    arg_parser.add_argument(
        "--min-words",
        default=10,
        type=int,
        metavar="COUNT",
        help="""A label must have this many words to make it into the expedition.""",
    )

    arg_parser.add_argument(
        "--notes",
        default="",
        metavar="TEXT",
        help="""Notes about this run. Enclose them in quotes.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
