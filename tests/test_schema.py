import polars as pl

def test_schema_order():
    from exptoolkit.data import BaseData, Column

    class A(BaseData):
        x = Column(pl.Float64)

    class B(A):
        y = Column(pl.Int64)

    assert list(B.schema.keys()) == ["x", "y"]


def test_missing_column_filled():
    from exptoolkit.data import BaseData, Column

    class A(BaseData):
        x = Column(pl.Float64)

    a = A({})
    assert a.table["x"].null_count() == 1


def test_drop_extra(sample_df):
    from conftest import SampleData

    df = {**sample_df, "extra": [1,2,3]}
    d = SampleData(df, drop_extra_columns=True)

    assert "extra" not in d.table.columns

    d = SampleData(df, drop_extra_columns=False)

    assert "extra" in d.table.columns
