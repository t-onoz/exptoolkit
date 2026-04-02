from __future__ import annotations
from typing import Protocol, Any, Literal, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

@runtime_checkable
class Target(Protocol):
    """Protocol for plotting graphs, absorbing differences in backends.
    The methods implement specific plotting commands."""

    def add_line(self,
                 x: ArrayLike,
                 y: ArrayLike,
                 color: Any = None,
                 label: str | None = None,
                 **kwargs) -> Any: ...
    def add_scatter(self,
                    x: ArrayLike,
                    y: ArrayLike,
                    c: ArrayLike | None = None,
                    label: str | None = None,
                    color_scale: Literal["log", "linear"] = "linear",
                    **kwargs) -> Any: ...
    def set_ax_label(self,
                     axis: Literal["x", "y"],
                     label: str) -> Any: ...
    def set_scale(self,
                  axis: Literal["x", "y"],
                  scale: Literal["linear", "log"]) -> Any: ...
    def set_title(self,
                  title: str) -> Any: ...
    def set_aspect(self,
                   aspect: Literal["equal", "auto"]) -> Any: ...
    def reverse_axis(self,
                     x: bool | None = None,
                     y: bool | None = None) -> Any: ...
    @classmethod
    def from_obj(cls, obj: Any) -> Target: ...
