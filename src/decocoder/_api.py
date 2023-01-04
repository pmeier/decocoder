from typing import *

import numpy as np

from . import _rs as rs


def segmentation_to_mask(
    segmentation: Union[Dict[str, List[int]], List[List[float]]],
    spatial_size: Optional[Tuple[int, int]] = None,
) -> np.ndarray:
    if isinstance(segmentation, dict):
        counts: List[int] = segmentation["counts"]
        size = cast(Tuple[int, int], tuple(segmentation["size"]))
        spatial_size = tuple(spatial_size)

        if spatial_size is None:
            spatial_size = size
        elif size != spatial_size:
            raise ValueError(
                f"implicit and explicit size mismatch: {size} != {spatial_size}",
            )

        return rle_to_mask(counts, spatial_size)
    else:
        polygons = segmentation

        if spatial_size is None:
            raise TypeError("`spatial_size` has to be passed")

        return polygons_to_mask(polygons, spatial_size)


def rle_to_mask(counts: List[int], spatial_size: Tuple[int, int]) -> np.ndarray:
    mask = np.zeros(spatial_size, dtype=np.uint8)
    rs.decode_rle(mask, counts)
    return mask


def polygons_to_mask(
    polygons: List[List[float]], spatial_size: Tuple[int, int]
) -> np.ndarray:
    mask = np.zeros(spatial_size, dtype=np.uint8)
    rs.decode_polygons(mask, polygons)
    return mask
