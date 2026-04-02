from __future__ import annotations
from typing import TYPE_CHECKING, Union, Any, Optional
from exptoolkit.plotter.backends._base import Target

if TYPE_CHECKING:
    # why "if TYPE_CHECKING"?
    # Because these imports are only needed for type checking
    # and would cause unnecessary dependencies at runtime.
    from typing import TypeAlias
    from matplotlib.axes import Axes
    from plotly.graph_objects import Figure
    from pyqtgraph import PlotWidget, PlotItem
    from openpyxl.worksheet.worksheet import Worksheet
    from openpyxl.chart import ScatterChart
    TargetLike: TypeAlias = Union[
        Target, Axes, Figure, tuple[Figure, int, int],
        PlotWidget, PlotItem,  Worksheet, tuple[Worksheet, Optional[ScatterChart]]
        ]
else:
    # At runtime, we don't need the specific types, so we can just use Any.
    TargetLike = Any

registry: dict[str, type[Target]] = {}

try:
    from exptoolkit.plotter.backends._matplotlib import MatplotlibTarget
    registry["matplotlib"] = MatplotlibTarget
except ImportError:
    pass

try:
    from exptoolkit.plotter.backends._plotly import PlotlyTarget
    registry["plotly"] = PlotlyTarget
except ImportError:
    pass

try:
    from exptoolkit.plotter.backends._pyqtgraph import PyQtGraphTarget
    registry["pyqtgraph"] = PyQtGraphTarget
except ImportError:
    pass

try:
    from exptoolkit.plotter.backends._openpyxl import OpenPyXlTarget
    registry["openpyxl"] = OpenPyXlTarget
except ImportError:
    pass

def get_target(obj: TargetLike) -> Target:
    """Create a Target instance from a given object by checking which backend it belongs to."""
    if isinstance(obj, Target):
        return obj
    for target_cls in registry.values():
        try:
            return target_cls.from_obj(obj)
        except (TypeError, ValueError):
            continue
    raise ValueError(f"Could not create Target from object: {obj}. "
                     f"Object does not match any registered backend targets."
                     f"Available backends: {list(registry.keys())}")
