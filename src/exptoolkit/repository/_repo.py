from __future__ import annotations
import re
import typing as t
from collections.abc import Iterable, Callable
from dataclasses import dataclass, field

@dataclass(frozen=True)
class DataResource:
    """
    Identifies an external resource as a string. `ref` can point to local files, URLs,
    or files inside archives (nested paths via "::" like "inner/path::archive.zip").
    The Resource itself holds no authentication or state; access and interpretation
    must be handled separately.

    `type_` represents additional information about a resource ("raw", "csv", etc.).
    """
    ref: str
    type_: str | None = field(hash=False, default=None, compare=False)


@dataclass(frozen=True)
class MeasurementID:
    value: t.Hashable

@dataclass(frozen=True)
class Measurement:
    id_: MeasurementID
    data: tuple[DataResource, ...]
    samples: tuple[str, ...]


class ResourceRepo:
    def __init__(self) -> None:
        self._ref2d: dict[str, DataResource] = {}

        # relations
        self._d2m: dict[DataResource, MeasurementID] = {}
        self._m2d: dict[MeasurementID, set[DataResource]] = {}

        # sample index
        self._sample2d: dict[str, set[DataResource]] = {}
        self._d2samples: dict[DataResource, set[str]] = {}

    def add(self, ref: str, *,
            measurement_id: t.Hashable,
            samples: str | Iterable[str],
            data_type: str | None = None
            ) -> DataResource:
        """Register a data source and its relations.

        Args:
            ref: reference to data resource
                (local files, URLs, or files inside archives as such).
            measurement_id: Measurement identifier.
            samples: Sample name(s).
            data_type: Optional data label.

        Returns:
            The registered DataSource.
        """
        dr = DataResource(ref, data_type)
        if isinstance(measurement_id, MeasurementID):
            mid = measurement_id
        else:
            mid = MeasurementID(measurement_id)

        # enforce many-to-one relation between DataResource and Measurement
        if dr in self._d2m:
            existing_mid = self._d2m[dr]
            if existing_mid != mid:
                raise ValueError(
                    f"DataResource {dr.ref} is already assigned to Measurement {existing_mid}, "
                    f"cannot reassign to {mid}."
                )

        self._ref2d.setdefault(ref, dr)
        self._d2m[dr] = mid
        self._m2d.setdefault(mid, set()).add(dr)

        if isinstance(samples, str):
            samples = [samples]
        else:
            samples = list(samples)
        self._d2samples.setdefault(dr, set())
        for s in samples:
            self._sample2d.setdefault(s, set()).add(dr)
            self._d2samples[dr].add(s)

        return dr

    def remove(self, ref: str) -> None:
        """Remove a data source and its relations.

        Args:
            ref: reference to data resource
                (local files, URLs, or files inside archives).
        """
        try:
            dr = self._ref2d.pop(ref)
        except KeyError as e:
            raise ValueError(f'{repr(ref)} does not exist in repository.') from e

        mid = self._d2m[dr]
        samples = self._d2samples[dr]

        self._d2m.pop(dr)
        self._m2d[mid].discard(dr)
        self._d2samples.pop(dr)
        for sample in samples:
            self._sample2d[sample].discard(dr)

        # remove measurement and samples if no data is associated
        if not self._m2d[mid]:
            self._m2d.pop(mid)
        for sample in samples:
            if not self._sample2d[sample]:
                self._sample2d.pop(sample)

    def move_resource(self, ref_before: str, ref_after: str) -> None:
        if ref_before not in self._ref2d:
            raise ValueError(f'{repr(ref_before)} does not exist in repository.')
        if ref_after in self._ref2d:
            raise ValueError(f'Cannot move resource because {repr(ref_after)} already exists.')

        dr_before = self._ref2d[ref_before]
        mid = self._d2m[dr_before]
        samples = self._d2samples[dr_before]
        data_type = dr_before.type_

        self.remove(ref_before)
        self.add(ref_after, measurement_id=mid, samples=samples, data_type=data_type)

    @t.overload
    def by_sample(self, sample, *, regex = ..., with_key: t.Literal[False] = False
    ) -> list[DataResource]: ...

    @t.overload
    def by_sample(self, sample, *, regex = ..., with_key: t.Literal[True] = True
    ) -> dict[str, list[DataResource]]: ...

    def by_sample(self, sample: str, *, regex=False, with_key=False):
        """Find measurements by sample name.

        Args:
            sample (str): Sample name or pattern.
            regex (bool, optional):
                If True, ``name`` is treated as a regular expression. This is slower but more flexible.
                Defaults to False.
            with_key (bool, optional):
                If False (default), returns a flat list of unique ``DataResource`` objects
                that match the query.

                If True, returns a mapping object from sample name to resources:
                ``dict[str, list[DataResource]]``
                 This is useful when you need to know which sample names were matched
                (especially in regex mode).
        """
        if regex:
            ptn = re.compile(sample)
            if with_key:
                return {s: list(dr_set)
                        for s, dr_set in self._sample2d.items()
                        if ptn.search(s)}
            return list({
                dr
                for s, dr_set in self._sample2d.items()
                for dr in dr_set
                if ptn.search(s)
                })
        if with_key:
            return {sample: list(self._sample2d.get(sample, set()))}
        return list(self._sample2d.get(sample, set()))

    def by_measurement(self, measurement_id: t.Hashable) -> list[DataResource]:
        """Return data sources belonging to a measurement.

        Args:
            measurement_id: Measurement identifier.

        Returns:
            Matching data sources.
        """
        return list(self._m2d.get(MeasurementID(measurement_id), set()))

    def measurement_of(self, resource: str | DataResource) -> MeasurementID:
        """Return the measurement of a data source.

        Args:
            resource: Data source.

        Returns:
            Associated measurement ID.
        """
        if isinstance(resource, str):
            resource = self._ref2d[resource]
        mid = self._d2m[resource]
        return mid

    def samples_of(self, resource: str | DataResource) -> list[str]:
        """Return samples associated with a data source.

        Args:
            resource: Data source.

        Returns:
            Associated sample names.
        """
        if isinstance(resource, str):
            resource = self._ref2d[resource]
        return list(self._d2samples.get(resource, set()))

    def find(self, f: Callable[[DataResource], bool]) -> list[DataResource]:
        """Return data sources matching a predicate.

        Args:
            f: Function taking a DataSource and returning bool.

        Returns:
            Matching data sources.
        """
        return [ds for ds in self._ref2d.values() if f(ds)]

    def as_list(self):
        return list(self._ref2d.values())

    def get_measurement(self, measurement_id: t.Hashable) -> Measurement:
        """Return a measurement view.

        Args:
            measurement_id: Measurement identifier.

        Returns:
            Measurement with its data sources.
        """
        mid = MeasurementID(measurement_id)
        if mid not in self._m2d:
            raise ValueError(f"Measurement {mid} does not exist in the repository.")
        data = tuple(self._m2d[mid])
        samples = tuple({s for dr in data for s in self._d2samples[dr]})
        return Measurement(id_=mid, data=data, samples=samples)

    def _check_indexes(self) -> None:
        """Verify internal index consistency. Raises AssertionError if any mismatch."""

        # 1. _d2m vs. _m2d
        for dr, mid in self._d2m.items():
            assert dr in self._m2d.get(mid, set()), f"{dr} missing in _m2d[{mid}]"

        for mid, dr_set in self._m2d.items():
            for dr in dr_set:
                assert self._d2m.get(dr) == mid, f"{dr} in _m2d[{mid}] but _d2m mismatch"

        # 2. _d2samples vs. _sample2d
        for dr, samples in self._d2samples.items():
            for s in samples:
                assert dr in self._sample2d.get(s, set()), f"{dr} missing in _sample2d[{s}]"

        for s, dr_set in self._sample2d.items():
            for dr in dr_set:
                assert s in self._d2samples.get(dr, set()), f"{s} missing in _d2samples[{dr}]"

        # 3. _ref2d
        for ref, dr in self._ref2d.items():
            assert ref == dr.ref, f"ref {repr(ref)} and dr.ref {(repr(dr.ref))} does not match"
            assert dr in self._d2m, f"{dr} missing in _d2m"
            assert dr in self._d2samples, f"{dr} missing in _d2samples"

        print("All indexes are consistent ✅")
