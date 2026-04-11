import polars as pl

def test_get(data):
    assert isinstance(data.x, pl.Series)


def test_set_sequence(data):
    data.x = [5, 6, 7]
    assert data.x.to_list() == [5, 6, 7]  # type: ignore


def test_set_expr(data):
    data.x = pl.col("x") * 2
    assert data.x.to_list() == [2, 4, 6]  # type: ignore


def test_set_scalar(data):
    data.x = 3
    assert data.x.to_list() == [3, 3, 3]  # type: ignore
