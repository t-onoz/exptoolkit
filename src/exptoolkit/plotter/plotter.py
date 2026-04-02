from __future__ import annotations
from string import capwords
from typing import Protocol, TypeVar, TYPE_CHECKING

from exptoolkit.data import BaseData
from exptoolkit.plotter.backends import get_target

if TYPE_CHECKING:
    from exptoolkit.plotter.backends import TargetLike

M_contra = TypeVar('M_contra', bound=BaseData, contravariant=True)

class Plotter(Protocol[M_contra]):
    def __call__(self, data: M_contra, target_like: TargetLike, *a, **kw) -> None: ...

def plot_xy(
    data: BaseData,
    target_like: TargetLike,
    xcol: str,
    ycol: str,
    xunit: str | None = None,
    yunit: str | None = None,
    label: str | None = None,
    add_ax_labels: bool = True,
):
    target = get_target(target_like)
    x = data.col_to_unit(xcol, xunit)
    y = data.col_to_unit(ycol, yunit)
    target.add_line(x, y, label=label)

    if add_ax_labels:
        xlabel = f"{capwords(xcol)} ({data.get_unit(xcol) if xunit is None else xunit})"
        ylabel = f"{capwords(ycol)} ({data.get_unit(ycol) if yunit is None else yunit})"
        target.set_ax_label("x", xlabel)
        target.set_ax_label("y", ylabel)

_plot_xy: Plotter = plot_xy
