from __future__ import annotations
import re
import typing as t
from pydantic import BaseModel, Field
import webcolors

ColorLike = t.Union["str", "tuple[float, float, float]", "tuple[float, float, float, float]"]

class Color(BaseModel):
    r: float = Field(ge=0.0, le=1.0)
    g: float = Field(ge=0.0, le=1.0)
    b: float = Field(ge=0.0, le=1.0)
    a: float = Field(1.0, ge=0.0, le=1.0)

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        super().__init__(r=r, g=g, b=b, a=a)

    @t.overload
    def as_rgb_int(self, include_alpha: t.Literal[False] = False) -> tuple[int, int, int]: ...

    @t.overload
    def as_rgb_int(self, include_alpha: t.Literal[True]) -> tuple[int, int, int, int]: ...

    def as_rgb_int(self, include_alpha=False):
        if include_alpha:
            return round(self.r * 255), round(self.g * 255), round(self.b * 255), round(self.a*255)
        return round(self.r * 255), round(self.g * 255), round(self.b * 255)

    @t.overload
    def as_rgb_float(self, include_alpha: t.Literal[False] = False) -> tuple[float, float, float]: ...

    @t.overload
    def as_rgb_float(self, include_alpha: t.Literal[True]) -> tuple[float, float, float, float]: ...

    def as_rgb_float(self, include_alpha=False):
        if include_alpha:
            return self.r, self.g, self.b, self.a
        return self.r, self.g, self.b

    def as_hex(self, include_alpha=False) -> str:
        r = round(self.r * 255)
        g = round(self.g * 255)
        b = round(self.b * 255)
        a = round(self.a * 255)
        if include_alpha:
            return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return f"#{r:02x}{g:02x}{b:02x}"


def parse_color(color: ColorLike) -> Color:
    """
    Normalize a color-like input to Color object.

    Accepts:
      - CSS color names ("red")
      - Hex strings (#rgb, #rgba, #rrggbb, #rrggbbaa)
      - tuple of 0-1 float (r, g, b) / (r, g, b, a)
      - "C{n}" (Matplotlib cycle)

    Conversions use webcolors.
    """

    # tuple / list
    if isinstance(color, (tuple, list)):
        if len(color) == 4:
            return Color(*color)
        if len(color) == 3:
            return Color(*color[:3])
        raise ValueError(f'tuple length must be 3 or 4 (given: {repr(color)})')

    # string
    if isinstance(color, str):
        s = color.strip().lower()

        # matplotlib C{n}
        m = re.fullmatch(r"c(\d+)", s)
        if m:
            import matplotlib as mpl
            s = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
            return parse_color(s[int(m.group(1)) % len(s)])

        # hex
        if s.startswith("#"):
            try:
                r, g, b = webcolors.hex_to_rgb(s)
                return Color(r/255, g/255, b/255)
            except ValueError:
                s = s.lstrip("#")
                if len(s) == 8:
                    return Color(
                        int(s[0:2], 16) / 255,
                        int(s[2:4], 16) / 255,
                        int(s[4:6], 16) / 255,
                        int(s[6:8], 16) / 255,
                    )
                if len(s) == 4:
                    r, g, b, a = [int(c * 2, 16) for c in s]
                    return Color(r / 255, g / 255, b / 255, a / 255)
            raise ValueError(f'Unknown hex code: {color}')
        # name
        r, g, b = webcolors.name_to_rgb(s)
        return Color(r / 255, g / 255, b / 255)

    raise TypeError(f'Unknown input type: {repr(type(color))}')

