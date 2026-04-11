import pytest

from exptoolkit.plotter.backends import get_target
from exptoolkit.plotter.backends._base import Target


def test_passthrough_target():
    class Dummy(Target):
        @classmethod
        def from_obj(cls, obj):
            return cls()

    obj = Dummy()
    assert get_target(obj) is obj


# --- matplotlib ---

@pytest.mark.skipif(
    pytest.importorskip("matplotlib", reason="matplotlib not installed") is None,
    reason="matplotlib not installed",
)
def test_matplotlib_figure():
    import matplotlib.pyplot as plt

    plt.figure()
    target = get_target(plt.gca())

    assert isinstance(target, Target)


# --- plotly ---

@pytest.mark.skipif(
    pytest.importorskip("plotly", reason="plotly not installed") is None,
    reason="plotly not installed",
)
def test_plotly_figure():
    import plotly.graph_objects as go

    fig = go.Figure()
    target = get_target(fig)

    assert isinstance(target, Target)



@pytest.mark.skipif(
    pytest.importorskip("plotly", reason="plotly not installed") is None,
    reason="plotly not installed",
)
def test_plotly_subplot():
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=2, cols=2)

    target = get_target((fig, 1, 2))

    assert isinstance(target, Target)


# --- openpyxl ---

@pytest.mark.skipif(
    pytest.importorskip("openpyxl", reason="openpyxl not installed") is None,
    reason="openpyxl not installed",
)
def test_openpyxl_worksheet():
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active

    target = get_target(ws)
    assert isinstance(target, Target)

# --- openpyxl ---

@pytest.mark.skipif(
    pytest.importorskip("pyqtgraph", reason="pyqtgraph not installed") is None,
    reason="pyqtgraph not installed",
)
def test_pyqtgraph():
    import pyqtgraph as pg
    pw = pg.plot(title="Three plot curves")

    target = get_target(pw)

    pw.close()
    assert isinstance(target, Target)


# --- failure cases ---

def test_no_backend_available(monkeypatch):
    import sys

    # remove all backends
    monkeypatch.setattr(sys, "modules", {})

    with pytest.raises(Exception):
        get_target(object())


def test_invalid_object():
    with pytest.raises(ValueError):
        get_target(object())
