import pytest
from hypothesis import given, strategies as st

import numpy as np

import decocoder
import decocoder._ref.pycocotools
import decocoder._ref.python


@st.composite
def rle_segmentations(
    draw,
    spatial_sizes=st.tuples(
        st.integers(min_value=2, max_value=100),
        st.integers(min_value=2, max_value=100),
    ),
):
    spatial_size = height, width = draw(spatial_sizes)
    num_pixels = height * width

    max_count = height // 2
    counts = np.random.randint(1, max_count + 1, 4 * max(num_pixels // max_count, 1))
    cumsum = counts.cumsum()

    idx = np.argmax(cumsum > num_pixels)
    counts = counts[:idx].tolist()
    missing = num_pixels - cumsum[idx - 1]
    if missing > 0:
        counts.append(missing)

    return {"counts": counts, "size": list(spatial_size)}, spatial_size


@pytest.mark.parametrize(
    "reference",
    [
        pytest.param(getattr(decocoder._ref, name), id=name)
        for name in ["python", "pycocotools"]
    ],
)
@given(st.data())
def test_against_reference(reference, data):
    segmentation, spatial_size = data.draw(rle_segmentations())

    actual = decocoder.segmentation_to_mask(segmentation, spatial_size)
    expected = reference.segmentation_to_mask(segmentation, spatial_size)

    np.testing.assert_array_equal(actual, expected)
