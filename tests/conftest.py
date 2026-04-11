import pytest
import polars as pl
from exptoolkit.data import BaseData, Column, Role

class SampleData(BaseData):
    x = Column(pl.Float64, base_unit="m", role=Role.EXTENSIVE)
    y = Column(pl.Float64, base_unit="s", role=Role.INTENSIVE)

@pytest.fixture
def sample_df():
    return {"x": [1.0, 2.0, 3.0], "y": [10.0, 20.0, 30.0]}

@pytest.fixture
def data(sample_df):
    return SampleData(sample_df)
