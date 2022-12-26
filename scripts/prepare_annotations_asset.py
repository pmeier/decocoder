import json
import pathlib
import re
import zipfile
from collections import defaultdict
from urllib.parse import urlsplit

import requests
import tqdm

PROJECT_ROOT = pathlib.Path(__file__).parents[1]
FILE_NAME_PATTERN = re.compile(r"instances_.*?[.]json")


def main(url, *, root):
    path = download(url, root=root)

    annotations = {}
    with zipfile.ZipFile(path) as zip_file:
        for zip_info in zip_file.infolist():
            file_name = pathlib.Path(zip_info.filename).name
            if not FILE_NAME_PATTERN.match(file_name):
                continue

            print(f"Load annotations from {file_name}")
            with zip_file.open(zip_info) as json_file:
                annotations.update(aggregate(json.load(json_file)))

    output_file = path.with_suffix(".json")
    print(f"Save annotations to {output_file}")
    with open(output_file, "w") as file:
        json.dump(annotations, file)


def download(url, root=".", *, name=None, chunk_size=32 * 1024):
    root = pathlib.Path(root)
    root.mkdir(exist_ok=True, parents=True)

    if not name:
        name = pathlib.Path(urlsplit(url).path).name

    path = root / name

    if not path.exists():
        print(f"Downloading {url} to {path}")
        with requests.get(url, stream=True) as response, open(path, "wb") as file:
            with tqdm.tqdm(
                total=int(response.headers["Content-Length"]),
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                dynamic_ncols=True,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

    return path


def aggregate(raw_data):
    spatial_sizes = {
        meta["id"]: (meta["height"], meta["width"]) for meta in raw_data["images"]
    }
    annotations = defaultdict(dict)
    for raw_annotation in raw_data["annotations"]:
        image_id = raw_annotation["image_id"]
        annotation_id = raw_annotation["id"]
        annotations[f"{image_id:012d}"][f"{annotation_id:012d}"] = (
            raw_annotation["segmentation"],
            spatial_sizes[image_id],
        )
    return dict(annotations)


if __name__ == "__main__":
    main(
        "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
        root=PROJECT_ROOT / "assets",
    )
