from __future__ import annotations
import typing as t
import sys
from importlib import import_module

from exptoolkit.plotter.backends._base import Target

if t.TYPE_CHECKING:
    # why "if TYPE_CHECKING"?
    # Because these imports are only needed for type checking
    # and would cause unnecessary dependencies at runtime.
    from matplotlib.axes import Axes
    from plotly.graph_objects import Figure
    from pyqtgraph import PlotWidget, PlotItem
    from openpyxl.worksheet.worksheet import Worksheet
    from openpyxl.chart import ScatterChart
    TargetLike = t.Union[
        Target, Axes, Figure, tuple[Figure, int, int],
        PlotWidget, PlotItem,  Worksheet, tuple[Worksheet, t.Optional[ScatterChart]]
        ]
else:
    # At runtime, we don't need the specific types, so we can just use Any.
    TargetLike = t.Any

_registry: dict[str, tuple[str, str]] = {
    # dependent package: (backend module, backend class)
    "matplotlib": ("exptoolkit.plotter.backends._matplotlib", "MatplotlibTarget"),
    "plotly": ("exptoolkit.plotter.backends._plotly", "PlotlyTarget"),
    "pyqtgraph": ("exptoolkit.plotter.backends._pyqtgraph", "PyQtGraphTarget"),
    "openpyxl": ("exptoolkit.plotter.backends._openpyxl", "OpenPyXlTarget"),
}

def get_target(obj: TargetLike) -> Target:
    """Create a Target instance from a given object by checking which backend it belongs to."""
    if isinstance(obj, Target):
        return obj
    available_backends: list[str] = []
    for pkg_name, (module_name, cls_name) in _registry.items():
        if pkg_name not in sys.modules:
            continue
        available_backends.append(pkg_name)
        module = import_module(module_name)
        cls: type[Target] = getattr(module, cls_name)
        try:
            return cls.from_obj(obj)
        except (TypeError, ValueError):
            continue
    raise ValueError(f"Could not create Target from object: {obj}. "
                     f"Object does not match any registered backend targets."
                     f"Available backends: {available_backends}")
