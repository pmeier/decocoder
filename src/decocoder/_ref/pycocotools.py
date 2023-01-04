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
    bool_mask = np.ascontiguousarray(pycocotools.mask.decode(rle))
    return np.multiply(bool_mask, 255, out=bool_mask)
