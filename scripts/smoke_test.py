import argparse
import json
import pathlib
import sys

import tqdm

import decocoder


def main(args):
    for path in tqdm.tqdm(args.files):
        with open(path) as file:
            data = json.load(file)

        spatial_sizes = {
            meta["id"]: (meta["height"], meta["width"]) for meta in data["images"]
        }

        for ann in tqdm.tqdm(data["annotations"]):
            try:
                decocoder.segmentation_to_mask(
                    ann["segmentation"], spatial_sizes[ann["image_id"]]
                )
            except BaseException as error:
                raise AssertionError(
                    f"The error above was caused by the annotation with ID {ann['id']} "
                    f"in file {path}."
                ) from error


def parse_argv(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument(dest="files", nargs="+", type=pathlib.Path)

    args = parser.parse_args(argv)

    args.files = [file.resolve() for file in args.files]

    return args


if __name__ == "__main__":
    args = parse_argv(sys.argv[1:])
    main(args)
