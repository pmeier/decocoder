from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pycocotools.mask


def segmentation_to_mask(
    segmentation: Union[Dict[str, List[int]], List[List[float]]],
    spatial_size: Optional[Tuple[int, int]],
) -> np.ndarray:
    if isinstance(segmentation, dict):
        rle = pycocotools.mask.frPyObjects(segmentation, *spatial_size)
    else:
        rle = pycocotools.mask.merge(
            pycocotools.mask.frPyObjects(segmentation, *spatial_size)
        )
    return np.ascontiguousarray(pycocotools.mask.decode(rle))
