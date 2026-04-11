import polars as pl

def test_roundtrip(data):
    b = data.normalize(10, "kg")
    c = b.denormalize()
    if hasattr(data.table, "frame_equal"):
        assert data.table.frame_equal(c.table)
    else:
        data.table.equals(c.table)


def test_intensive_not_changed():
    from exptoolkit.data import BaseData, Column, Role

    class A(BaseData):
        x = Column(pl.Float64, role=Role.INTENSIVE)

    a = A({"x":[10]})
    b = a.normalize(10, "kg")

    assert b.x[0] == 10


def test_normalize_extensive():
    from exptoolkit.data import BaseData, Column, Role

    class A(BaseData):
        x = Column(pl.Float64, role=Role.EXTENSIVE)

    a = A({"x": [10.0, 20.0]})
    b = a.normalize(10, "kg")

    assert b.x.to_list() == [1.0, 2.0]

def test_normalize_inverse_extensive():
    from exptoolkit.data import BaseData, Column, Role

    class A(BaseData):
        x = Column(pl.Float64, role=Role.INVERSE_EXTENSIVE)

    a = A({"x": [10.0, 20.0]})
    b = a.normalize(10, "kg")

    assert b.x.to_list() == [100.0, 200.0]


def test_double_normalize_error(data):
    b = data.normalize(10, "kg")

    import pytest
    with pytest.raises(ValueError):
        b.normalize(5, "kg")
