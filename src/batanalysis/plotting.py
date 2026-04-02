from __future__ import annotations
from typing import TYPE_CHECKING, Literal
from string import capwords
import polars as pl
from exptoolkit.plotter import get_target, Plotter, TargetLike
from batanalysis.data import ChargeDischargeData, State, EISData, CycleSummaryData
from batanalysis.processing import integrate_capacity, differentiate, calc_z_theta


def plot_charge_discharge(
    data: ChargeDischargeData,
    target_like: TargetLike,
    *,
    cycle: int | None = None,
    label: str | None = None,
    add_ax_labels: bool = True,
    mode: Literal['step', 'cycle', 'total'] = 'step',
    **kw
):
    target = get_target(target_like)
    cls = ChargeDischargeData
    if not data.is_col_ready(cls.step_capacity.name):
        integrate_capacity(data)

    data = data if cycle is None else data.filter(cycle=cycle)
    if mode == 'step':
        x_expr = (pl.when(cls.state.expr.is_in([State.CHARGE, State.DISCHARGE]))
            .then(cls.step_capacity.expr)
            .otherwise(None)
        )
    elif mode == 'cycle':
        x_expr = cls.cycle_capacity.expr
    else:
        x_expr = cls.capacity.expr
    df = data.table.select(
        x_expr.alias('x'),
        cls.voltage.expr,
    )
    x = df['x']
    y = df[cls.voltage.name]
    target.add_line(x, y, label=label, **kw)
    if add_ax_labels:
        target.set_ax_label('x', f'Capacity ({data.get_unit("step_capacity")})')
        target.set_ax_label('y', f'Volatge ({data.get_unit("voltage")})')

def plot_dqdv(
    data: ChargeDischargeData,
    target_like: TargetLike,
    *,
    label: str | None = None,
    add_ax_labels: bool = True,
    cycle: int | None = None,
    **kw
):
    cls = ChargeDischargeData
    if not data.is_col_ready(cls.dqdv.name):
        differentiate(data)
    data = data if cycle is None else data.filter(cycle=cycle)
    target = get_target(target_like)
    target.add_line(
        x = data.voltage,
        y = data.dqdv,
        label = label,
        **kw,
    )
    if add_ax_labels:
        target.set_ax_label('x', f'Voltage ({data.get_unit(cls.voltage.name)})')
        target.set_ax_label('y', f'dQ/dV ({data.get_unit(cls.dqdv.name)})')

def plot_colecole(
    data: EISData,
    target_like: TargetLike,
    *,
    label: str | None = None,
    add_ax_labels: bool = True,
    set_aspect: bool = True,
    **kw
):
    target = get_target(target_like)
    cls = EISData
    x = data.re_Z
    y = data.im_Z
    target.add_scatter(x, y, label=label, **kw)
    target.reverse_axis(y=True)
    if add_ax_labels:
        target.set_ax_label("x", f"Re[Z] ({data.get_unit(cls.re_Z.name)})")
        target.set_ax_label("y", f"Im[Z] ({data.get_unit(cls.im_Z.name)})")
    if set_aspect:
        target.set_aspect("equal")

def plot_bode_theta(
    data: EISData,
    target_like: TargetLike,
    *,
    label: str | None = None,
    add_ax_labels :bool = True,
    **kw
):
    target = get_target(target_like)
    cls = EISData
    if not data.is_col_ready(cls.theta.name):
        calc_z_theta(data)
    x = data.frequency
    y = data.col_to_unit(cls.theta.name, 'deg')
    target.add_line(x, y, label=label, **kw)
    target.set_scale('x', 'log')
    if add_ax_labels:
        target.set_ax_label("x", f"Frequency ({data.get_unit(cls.frequency.name)})")
        target.set_ax_label("y", "theta (deg.)")

def plot_bode_z(
    data: EISData,
    target_like: TargetLike,
    *,
    label: str | None = None,
    add_ax_labels :bool = True,
    **kw
):
    target = get_target(target_like)
    cls = EISData
    if not data.is_col_ready(cls.abs_Z.name):
        calc_z_theta(data)
    x = data.frequency
    y = data.abs_Z
    target.add_line(x, y, label=label, **kw)
    target.set_scale('x', 'log')
    if add_ax_labels:
        target.set_ax_label("x", f"Frequency ({data.get_unit(cls.frequency.name)})")
        target.set_ax_label("y", f"|Z| ({data.get_unit(cls.abs_Z.name)})")

def plot_cycle(
    data: CycleSummaryData,
    target_like: TargetLike,
    *,
    label: str | None = None,
    state: Literal['charge', 'discharge'] = 'discharge',
    mode: Literal['retention', 'absolute'] = 'retention',
    value: Literal['capacity', 'energy'] = 'capacity',
    add_ax_labels: bool = True,
    **kw,
):
    target = get_target(target_like)
    data = data.filter(state=state)
    x = data.cycle
    col_y = f'{value}_retention' if mode == 'retention' else value
    unit = 'percent' if mode == 'retention' else None
    y = data.col_to_unit(col_y, unit)
    target.add_line(x, y, label=label, **kw)
    if add_ax_labels:
        target.set_ax_label('x', 'Cycle Number')
        ylabel = capwords(state) + ' '
        ylabel += capwords(col_y.replace('_', ' '))
        ylabel += f' ({"%" if mode == "retention" else data.get_unit(col_y)})'
        target.set_ax_label('y', ylabel)

if TYPE_CHECKING:
    _plot_charge_discharge: Plotter[ChargeDischargeData] = plot_charge_discharge
    _plot_dqdv: Plotter[ChargeDischargeData] = plot_dqdv
    _plot_colecole: Plotter[EISData] = plot_colecole
    _plot_bode_theta: Plotter[EISData] = plot_bode_theta
    _plot_bode_z: Plotter[EISData] = plot_bode_z
    _plot_cycle: Plotter[CycleSummaryData] = plot_cycle
