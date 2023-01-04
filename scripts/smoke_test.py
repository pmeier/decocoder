import argparse
import pathlib
import sys

import annotations_asset

import decocoder

PROJECT_ROOT = pathlib.Path(__file__).parents[1]


def main(args):
    for segmentation, spatial_size in annotations_asset.load(args.annotations_file):
        try:
            decocoder.segmentation_to_mask(segmentation, spatial_size)
        except BaseException as error:
            raise AssertionError(
                f"decocoder.segmentation_to_mask(segmentation, spatial_size) "
                f"failed for the following inputs:\n\n"
                f"segmentation: {segmentation}\n"
                f"spatial_size: {spatial_size}\n"
            ) from error


def parse_argv(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--annotations-file",
        type=pathlib.Path,
        default=PROJECT_ROOT / "assets" / "annotations_trainval2017.json",
    )

    args = parser.parse_args(argv)

    args.annotations_file = args.annotations_file.resolve()

    return args


if __name__ == "__main__":
    args = parse_argv(sys.argv[1:])
    main(args)
