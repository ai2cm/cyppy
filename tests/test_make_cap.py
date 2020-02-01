import os
import pytest
import os.path
import sys


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
LIB_DIR = os.path.join(TEST_DIR, '../lib')

sys.path.append(LIB_DIR)
import make_cap


@pytest.mark.parametrize(
    "dim_tuple, target",
    [
        pytest.param(
            (),
            "",
            id="empty"
        ),
        pytest.param(
            ('dim1',),
            "(:)",
            id="1D"
        ),
        pytest.param(
            ('dimension1', 'dimension2'),
            "(:,:)",
            id="2D",
        ),
        pytest.param(
            ('dim1', 'dim2', 'dim3', 'dim4'),
            "(:,:,:,:)",
            id="4D"
        ),
    ]
)
def test_get_colon_dimension_string(dim_tuple, target):
    result = make_cap.get_colon_dimension_string(dim_tuple)
    assert result == target
