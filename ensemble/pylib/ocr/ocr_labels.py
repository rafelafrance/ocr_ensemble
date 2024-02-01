import argparse
import logging
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
    args.text_dir.mkdir(parents=True, exist_ok=True)

    ensemble = Ensemble(**vars(args))

    paths = sorted(args.label_dir.glob("*"))
    for path in tqdm(paths):
        with warnings.catch_warnings():  # Turn off EXIF warnings
            warnings.filterwarnings("ignore", category=UserWarning)

            try:
                label = Image.open(path).convert("RGB")
                text = await ensemble.run(label)

            except IMAGE_EXCEPTIONS as err:
                msg = f"Could not prepare {path.name}: {err}"
                logging.exception(msg)
                continue

        with (args.text_dir / f"{path.stem}.txt").open("w") as f:
            f.write(text)
