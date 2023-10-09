#!/usr/bin/env python3
import argparse
import asyncio
import textwrap
from pathlib import Path

from pylib.ocr import ocr_labels
from traiter.pylib import log


async def main():
    log.started()
    args = parse_args()
    await ocr_labels.ocr_labels(args)
    log.finished()


def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """OCR images of labels. (Try this ensemble: -RrDdbnPp)"""
        ),
    )

    arg_parser.add_argument(
        "--label-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Directory containing the labels to OCR.""",
    )

    arg_parser.add_argument(
        "--text-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Output OCR text files to this directory.""",
    )

    arg_parser.add_argument(
        "-R",
        "--none-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that runs EasyOCR without image
            manipulation.""",
    )

    arg_parser.add_argument(
        "-r",
        "--none-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that runs Tesseract without image
            manipulation.""",
    )

    arg_parser.add_argument(
        "-D",
        "--deskew-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that deskews the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "-d",
        "--deskew-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that deskews the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "-B",
        "--binarize-easyocr",
        action="store_true",
        help="""Add a step to the OCR pipeline that binarizes the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "--binarize-tesseract",
        "-b",
        action="store_true",
        help="""Add a step to the OCR pipeline that binarizes the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "--denoise-easyocr",
        "-N",
        action="store_true",
        help="""Add a step to the OCR pipeline that denoises the label image before
            running EasyOCR.""",
    )

    arg_parser.add_argument(
        "-n",
        "--denoise-tesseract",
        action="store_true",
        help="""Add a step to the OCR pipeline that denoises the label image before
            running Tesseract.""",
    )

    arg_parser.add_argument(
        "-P",
        "--pre-process",
        action="store_true",
        help="""Add a step to the OCR pipeline that pre-processes the OCR text before
            the building the consensus sequence. This step performs simple text
            substitutions that may help build the consensus sequence.""",
    )

    arg_parser.add_argument(
        "-p",
        "--post-process",
        action="store_true",
        help="""Add a step to the OCR pipeline that post-processes the OCR text
            sequence with a spell checker etc. after building the consensus sequence.
            """,
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    asyncio.run(main())
