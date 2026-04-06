from __future__ import annotations
import polars as pl
from exptoolkit.data import BaseData, Role, Column

class State:
    CHARGE = 'charge'
    DISCHARGE = 'discharge'
    REST = 'rest'
    UNKNOWN = 'unknown'


class ChargeDischargeData(BaseData):
    time = Column(pl.Float64, 's', Role.INTENSIVE)
    cycle = Column(pl.UInt16, 'dimensionless', Role.INTENSIVE)
    step = Column(pl.UInt32, 'dimensionless', Role.INTENSIVE)
    state = Column(
        pl.Enum(['charge', 'discharge', 'rest', 'unknown']),
        'dimensionless',
        Role.INTENSIVE
    )
    temperature = Column(pl.Float32, 'degC', Role.INTENSIVE)
    current = Column(pl.Float32, 'mA', Role.EXTENSIVE)
    capacity = Column(pl.Float32, 'mAh', Role.EXTENSIVE)
    energy = Column(pl.Float32, 'mWh', Role.EXTENSIVE)
    cycle_time = Column(pl.Float64, 's', Role.INTENSIVE)
    cycle_capacity = Column(pl.Float32, 'mAh', Role.EXTENSIVE)
    cycle_energy = Column(pl.Float32, 'mWh', Role.EXTENSIVE)
    step_time = Column(pl.Float64, 's', Role.INTENSIVE)
    step_capacity = Column(pl.Float32, 'mAh', Role.EXTENSIVE)
    step_energy = Column(pl.Float32, 'mWh', Role.EXTENSIVE)
    voltage = Column(pl.Float32, 'V', Role.INTENSIVE)
    dqdv = Column(pl.Float32, 'mAh/V', Role.EXTENSIVE)
    dvdq = Column(pl.Float32, 'V/mAh', Role.EXTENSIVE)

class CycleSummaryData(BaseData):
    cycle = Column(pl.UInt16, 'dimensionless', Role.INTENSIVE)
    state = Column(pl.Enum(['charge', 'discharge']), 'dimensionless', Role.INTENSIVE)
    capacity = Column(pl.Float32, 'mAh', Role.EXTENSIVE)
    capacity_retention = Column(pl.Float32, 'dimensionless', Role.INTENSIVE)
    coulomb_efficiency = Column(pl.Float32, 'dimensionless', Role.INTENSIVE)
    energy = Column(pl.Float32, 'mWh', Role.EXTENSIVE)
    energy_efficiency = Column(pl.Float32, 'dimensionless', Role.INTENSIVE)
    energy_retention = Column(pl.Float32, 'dimensionless', Role.INTENSIVE)


class EISData(BaseData):
    frequency = Column(pl.Float32, "Hz", Role.INTENSIVE)
    re_Z = Column(pl.Float32, "ohm", Role.INVERSE_EXTENSIVE)
    im_Z = Column(pl.Float32, "ohm", Role.INVERSE_EXTENSIVE)
    abs_Z = Column(pl.Float32, "ohm", Role.INVERSE_EXTENSIVE)
    theta = Column(pl.Float32, "rad", Role.INTENSIVE)
