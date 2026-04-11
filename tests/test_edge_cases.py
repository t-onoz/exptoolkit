import pytest
import polars as pl
from exptoolkit.data import BaseData, Column

def test_dtype_mismatch():
    class A(BaseData):
        x = Column(pl.Float64)

    with pytest.raises(Exception):
        A(pl.DataFrame({"x": ["a"]}))


def test_empty():
    class A(BaseData):
        x = Column(pl.Float64)

    a = A({"x": []})
    assert len(a.table) == 0


def test_nan_normalization(data):
    b = data.normalize(float("nan"), "kg")
    assert b.norm.unit == "kg"
