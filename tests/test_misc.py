import pytest

from ansys.tools.path.misc import is_float

values = [
    (11, True),
    (11.1, True),
    ("asdf", False),
    ("1234asdf", False),
]


@pytest.mark.parametrize("values", values)
def test_is_float(values):
    assert is_float(values[0]) == values[1]
