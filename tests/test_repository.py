# pylint: disable=W
import pytest
from exptoolkit.repository import ResourceRepo  # type: ignore[import]
from exptoolkit.repository._repo import MeasurementID  # type: ignore[import]
from tempfile import NamedTemporaryFile

def test_add_and_lookup():
    repo = ResourceRepo()
    dr1 = repo.add("file1", measurement_id="m1", samples="s1", data_type="csv")
    dr2 = repo.add("file2", measurement_id="m1", samples=["s1", "s2"], data_type="txt")
    repo._check_indexes()

    # Measurement lookup
    m1 = repo.by_measurement("m1")
    assert dr1 in m1
    assert dr2 in m1
    assert len(m1) == 2

    # Sample lookup
    s1_set = repo.by_sample("s1")
    assert dr1 in s1_set and dr2 in s1_set
    s2_set = repo.by_sample("s2")
    assert dr2 in s2_set
    assert dr1 not in s2_set

    # Samples of DataSource
    assert "s1" in repo.samples_of(dr1)
    assert "s2" not in repo.samples_of(dr1)
    assert "s1" in repo.samples_of(dr2)
    assert "s2" in repo.samples_of(dr2)


def test_remove():
    repo = ResourceRepo()
    dr = repo.add("file1", measurement_id="m1", samples="s1")

    assert "file1" in repo._ref2d
    assert dr in repo._d2m
    assert dr in repo._m2d.get(MeasurementID("m1"), set())
    assert dr in repo._sample2d.get("s1", set())
    assert dr in repo._ref2d.values()
    assert MeasurementID("m1") in repo._m2d
    assert "s1" in repo._sample2d

    repo.remove("file1")
    repo._check_indexes()

    # Index cleanup
    assert "file1" not in repo._ref2d
    assert dr not in repo._d2m
    assert dr not in repo._m2d.get(MeasurementID("m1"), set())
    assert dr not in repo._sample2d.get("s1", set())
    assert dr not in repo._ref2d.values()
    assert MeasurementID("m1") not in repo._m2d
    assert "s1" not in repo._sample2d

def test_move_resource():
    repo = ResourceRepo()
    repo.add("file1", measurement_id="m1", samples=["s1", "s2"], data_type="csv")
    repo.move_resource("file1", "file_new")
    repo._check_indexes()

    # old ref gone
    assert "file1" not in repo._ref2d

    # new ref exists
    dr_new = repo._ref2d["file_new"]
    assert dr_new.ref == "file_new"
    assert repo._d2m[dr_new].value == "m1"
    assert "s1" in repo.samples_of(dr_new)
    assert "s2" in repo.samples_of(dr_new)
    assert dr_new in repo.by_sample("s1")
    assert dr_new in repo.by_measurement("m1")


def test_find_predicate():
    repo = ResourceRepo()
    dr1 = repo.add("file1", measurement_id="m1", samples="s1", data_type="csv")
    dr2 = repo.add("file2", measurement_id="m1", samples="s1", data_type="txt")
    repo._check_indexes()

    # Find by type
    csv_set = repo.find(lambda dr: dr.type_ == "csv")
    assert dr1 in csv_set
    assert dr2 not in csv_set


def test_empty_lookup():
    repo = ResourceRepo()
    assert not repo.by_sample("nope")
    assert not repo.by_measurement("none")
    assert not repo.find(lambda dr: False)


def test_multiple_measurements():
    repo = ResourceRepo()
    dr1 = repo.add("file1", measurement_id="m1", samples="s1")
    dr2 = repo.add("file2", measurement_id="m2", samples="s1")
    repo._check_indexes()

    # by sample
    s1_set = repo.by_sample("s1")
    assert dr1 in s1_set and dr2 in s1_set

    # by measurement
    m1_set = repo.by_measurement("m1")
    assert dr1 in m1_set
    assert dr2 not in m1_set

def test_save_and_load():
    repo = ResourceRepo()
    dr1 = repo.add("file1", measurement_id="m1", samples="s1")
    dr2 = repo.add("file2", measurement_id="m2", samples="s1")
    repo._check_indexes()

    with NamedTemporaryFile(mode='w+') as tmp:
        repo.save(tmp)
        tmp.seek(0)
        repo2 = ResourceRepo.load(tmp)

    repo2._check_indexes()
    assert dr1 in repo2.as_list()
    assert dr2 in repo2.as_list()
    assert "s1" in repo2._sample2d
    assert MeasurementID("m1") in repo2._m2d
    assert MeasurementID("m2") in repo2._m2d
