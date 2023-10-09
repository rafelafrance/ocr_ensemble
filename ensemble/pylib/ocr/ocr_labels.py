import argparse
import logging
import os
import warnings

from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

from .ensemble import Ensemble

IMAGE_EXCEPTIONS = (
    UnidentifiedImageError,
    ValueError,
    TypeError,
    FileNotFoundError,
    OSError,
)


async def ocr_labels(args: argparse.Namespace) -> None:
    os.makedirs(args.text_dir, exist_ok=True)

    ensemble = Ensemble(**vars(args))

    paths = sorted(args.label_dir.glob("*"))
    for path in tqdm(paths):
        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)

            try:
                label = Image.open(path).convert("RGB")
                text = await ensemble.run(label)

            except IMAGE_EXCEPTIONS as err:
                logging.error(f"Could not prepare {path.name}: {err}")
                continue

        with open(args.text_dir / f"{path.stem}.txt", "w") as f:
            f.write(text)
