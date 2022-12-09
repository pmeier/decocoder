import argparse
import json
import pathlib
import sys

import tqdm

import decocoder

PROJECT_ROOT = pathlib.Path(__file__).parents[1]


def main(args):
    print(f"Loading annotations from {args.annotations_file}")
    with open(args.annotations_file) as file:
        annotations = json.load(file)

    with tqdm.tqdm(total=len(annotations)) as progress_bar:
        for file_name, per_file_annotations in annotations.items():
            progress_bar.desc = file_name
            progress_bar.display()

            for annotation_id, (segmentation, spatial_size) in tqdm.tqdm(
                per_file_annotations.items(), total=len(per_file_annotations)
            ):
                try:
                    decocoder.segmentation_to_mask(segmentation, spatial_size)
                except BaseException as error:
                    raise AssertionError(
                        f"The error above was caused by "
                        f"the annotation with ID {annotation_id} in file {file_name}."
                    ) from error

            progress_bar.update()


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
