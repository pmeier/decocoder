import argparse
import json
import pathlib
import sys

import tqdm
import decocoder

PROJECT_ROOT = pathlib.Path(__file__).parents[1]


def main(args):
    for segmentation, spatial_size in load_annotations(args.annotations_file):
        try:
            decocoder.segmentation_to_mask(segmentation, spatial_size)
        except BaseException as error:
            raise AssertionError(
                f"decocoder.segmentation_to_mask(segmentation, spatial_size) "
                f"failed for the following inputs:\n\n"
                f"segmentation: {segmentation}\n"
                f"spatial_size: {spatial_size}\n"
            ) from error


def load_annotations(path):
    print(f"Loading annotations from {path}")
    with open(path) as file:
        annotations = json.load(file)
    with tqdm.tqdm(
        total=sum(len(image_annotations) for image_annotations in annotations.values())
    ) as progress_bar:
        for image_id, image_annotations in annotations.items():
            for annotation_id, annotation in image_annotations.items():
                progress_bar.desc = (
                    f"image_id={image_id} / annotation_id={annotation_id}"
                )
                progress_bar.display()

                try:
                    yield annotation
                finally:
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
