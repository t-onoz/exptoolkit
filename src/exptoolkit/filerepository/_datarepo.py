from __future__ import annotations
import re
from os import PathLike
from collections.abc import Callable, Hashable
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path


@dataclass(frozen=True)
class DataFile:
    """a reference to a file containing measurement data"""
    rel_path: str
    data_type: str  # a string which represents a kind of measurement.

    def __post_init__(self):
        if isinstance(self.rel_path, PathLike):
            p = Path(self.rel_path)
            if p.is_absolute():
                raise ValueError("rel_path must be a relative path")
            object.__setattr__(self, "rel_path", p.as_posix())

    def full_path(self, root: PathLike | str) -> Path:
        return Path(root) / self.rel_path

    @classmethod
    def from_full_path(
            cls,
            path: PathLike | str,
            root: PathLike | str,
            data_type: str,
            resolve_path: bool = False,
    ) -> DataFile:
        path = Path(path)
        root = Path(root)
        if resolve_path:
            path = path.resolve()
            root = root.resolve()
        rel_path = path.relative_to(root).as_posix()
        return cls(rel_path, data_type)


@dataclass(frozen=True)
class Measurement:
    """metadata and associated data files for a measurement.
    one measurement can contain multiple files."""
    request_id: Hashable
    measurement_id: Hashable
    sample_name: str
    files: set[DataFile] = field(default_factory=set, repr=False)
    conditions: dict[str, Any] = field(default_factory=dict)
    _hash: int = field(init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, '_hash', hash(self.key))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Hashable):
            return hash(self) == hash(other)
        return False

    @property
    def key(self) -> tuple[Hashable, Hashable, str]:
        return self.request_id, self.measurement_id, self.sample_name

@dataclass
class MeasurementRepo:
    """an indexed collection of measurements that supports efficient lookup operations"""
    root : str
    _measurements: dict[Measurement, Measurement] = \
        field(default_factory=dict, repr=False, init=False)
    _by_request_id: dict[Hashable, set[Measurement]] = \
        field(default_factory=dict, repr=False, init=False)
    _by_measurement_id: dict[Hashable, set[Measurement]] = \
        field(default_factory=dict, repr=False, init=False)
    _by_sample_name: dict[str, set[Measurement]] = \
        field(default_factory=dict, repr=False, init=False)
    _by_data_file: dict[DataFile, set[Measurement]] = \
        field(default_factory=dict, repr=False, init=False)

    def __post_init__(self):
        full_root = Path(self.root).resolve().as_posix()
        object.__setattr__(self, "root", full_root)

    def add_file(
            self, *,
            key: tuple[Hashable, Hashable, str] | Measurement,
            path: PathLike | str,
            data_type: str,
            resolve_path: bool = False,
        ) -> Measurement:
        """

        :param key: tuple of (req_id, meas_id, sample_name), or a Measurement
        :param sample_name: string
        :param path: full path to the file
        :param data_type: string representing the type of data
        :param resolve_path: if True, resolves path before adding.
        :return: Measurement
        """
        if isinstance(key, Measurement):
            req_id, meas_id, sample_name = key.request_id, key.measurement_id, key.sample_name
        else:
            req_id, meas_id, sample_name = key
        path = Path(path)
        if resolve_path:
            path = path.resolve()
        file = DataFile.from_full_path(path=path, root=self.root, data_type=data_type)
        _m = Measurement(req_id, meas_id, sample_name)
        m = self._measurements.setdefault(_m, _m)
        m.files.add(file)
        self._by_request_id.setdefault(req_id, set()).add(m)
        self._by_measurement_id.setdefault(meas_id, set()).add(m)
        self._by_sample_name.setdefault(sample_name, set()).add(m)
        self._by_data_file.setdefault(file, set()).add(m)
        return m

    def remove_file(
            self, *,
            path: PathLike | str,
            data_type: str,
            resolve_path: bool = False,
    ):
        """scans index for file, and removes all entries."""
        path = Path(path)
        if resolve_path:
            path = path.resolve()
        file = DataFile.from_full_path(path=path, root=self.root, data_type=data_type)
        for m in self._by_data_file.pop(file, set()):
            m.files.discard(file)

    def find_by_sample(self, name: str, regex=False) -> list[Measurement]:
        """scans index by sample name.

        Args:
            name (str): sample name
            regex (bool, optional): if True, name is regarded as regex (`re.search`).
                slow, but far more flexible. Defaults to False.
        """
        if regex:
            ptn = re.compile(name)
            return [
                m
                for name, m_set in self._by_sample_name.items()
                for m in m_set
                if re.search(ptn, name)
            ]
        return list(self._by_sample_name.get(name, []))

    def find_by_request(self, id_: Hashable) -> list[Measurement]:
        return list(self._by_request_id.get(id_, []))

    def find_by_measurement(self, id_: Hashable) -> list[Measurement]:
        return list(self._by_measurement_id.get(id_, []))

    def find(self, f: Callable[[Measurement], bool]) -> list[Measurement]:
        """Filters by arbitrary function."""
        return [m for m in self if f(m)]

    def __iter__(self):
        return iter(self._measurements)

    def rebuild_indexes(self):
        self._by_request_id = {}
        self._by_measurement_id = {}
        self._by_sample_name = {}
        self._by_data_file = {}
        for m in self._measurements:
            self._by_request_id.setdefault(m.request_id, {m}).add(m)
            self._by_measurement_id.setdefault(m.measurement_id, {m}).add(m)
            self._by_sample_name.setdefault(m.sample_name, {m}).add(m)
            for file in m.files:
                self._by_data_file.setdefault(file, {m}).add(m)
