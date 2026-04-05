from __future__ import annotations
import os
import time
import typing as t
import json
from pathlib import Path
from logging import getLogger
from pydantic import BaseModel

from exptoolkit.repository import ScanResult, ResourceScanner

logger = getLogger(__name__)

class _CacheEntry(BaseModel):
    mtime: float
    scanned_at: float
    results: list[ScanResult]


class DirectoryMeasurementScanner(ResourceScanner):
    """
    Example scanner for a directory with structure:

        root/
            measurement_id_1/
                sample1.csv
                sample2.csv
            measurement_id_2/
                ...

    - measurement_id = folder name
    - sample_name = file name without ".csv"
    - ref = relative path from root (no resolve)

    Uses per-measurement cache based on folder mtime.
    """

    def __init__(self, root: str | os.PathLike):
        self.root = Path(root)
        self._cache: dict[str, _CacheEntry] = {}

    # --- ownership ---
    def owns(self, ref: str) -> bool:
        return True

    # --- main scan ---
    def scan(self) -> list[ScanResult]:
        results: list[ScanResult] = []

        with os.scandir(self.root) as it:
            for entry in it:
                if not entry.is_dir():
                    continue

                measurement_id = entry.name

                # NOTE:
                # entry.stat() is fast but may return stale mtime (Windows / FS cache).
                # This can occur even without concurrent writes (see CPython issue #85278).
                # Calling os.stat(path) seems to refresh it; use that if strict correctness is needed.
                mtime = entry.stat().st_mtime

                # check cache
                cache = self._cache.get(measurement_id)
                if cache and cache.mtime == mtime:
                    logger.info('read measurement %r from cache', measurement_id)
                    results.extend(cache.results)
                    continue

                logger.info('read measurement %r from disk', measurement_id)

                # scan files
                scanned = self._scan_measurement_dir(entry.path, measurement_id)

                # update cache
                self._cache[measurement_id] = _CacheEntry(
                    mtime=mtime,
                    scanned_at=time.time(),
                    results=scanned,
                )

                results.extend(scanned)

        return results

    # --- internal ---
    def _scan_measurement_dir(self, d: str, measurement_id: str) -> list[ScanResult]:
        results: list[ScanResult] = []

        for f in os.scandir(d):
            if not f.is_file():
                continue

            if not f.name.endswith(".csv"):
                continue

            sample_name = f.name[:-4]  # strip ".csv"

            ref = f.path

            results.append(
                ScanResult(
                    ref=ref,
                    measurement_id=measurement_id,
                    samples=(sample_name,),
                    data_type="csv",
                )
            )

        return results

    def save_cache(self, file: str | os.PathLike | t.IO[str], **json_kw) -> None:
        """Save the cache as a JSON file."""
        data: dict[str, dict[str, t.Any]]  = {
            mid: entry.model_dump(mode='json') for mid, entry in self._cache.items()
        }
        json_kw.setdefault('indent', 2)
        json_kw.setdefault('ensure_ascii', False)
        if isinstance(file, (str, os.PathLike)):
            with open(file, "w", encoding='utf-8') as f:
                json.dump(data, f, **json_kw)
        else:
            json.dump(data, file, **json_kw)

    def load_cache(self, file: str | os.PathLike | t.IO[str]) -> None:
        if isinstance(file, (str, os.PathLike)):
            with open(file, "w", encoding='utf-8') as f:
                data: dict[str, dict[str, t.Any]] = json.load(f)
        else:
            data = json.load(file)
        self._cache.update({mid: _CacheEntry(**dct) for mid, dct in data.items()})


if __name__ == "__main__":
    import logging
    import sys
    import io
    from pprint import pprint
    from tempfile import TemporaryDirectory
    from exptoolkit.repository import ResourceRepo

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    with TemporaryDirectory() as tmpdir:
        repo = ResourceRepo()
        p = Path(tmpdir)
        (p / 'm001').mkdir()
        (p / 'm002').mkdir()
        (p / 'm001' / 'sample1.csv').touch()
        (p / 'm001' / 'sample2.csv').touch()
        (p / 'm002' / 'sample3.csv').touch()
        (p / 'm002' / 'sample4.csv').touch()

        os.stat(p / 'm001')
        os.stat(p / 'm002')

        scanner = DirectoryMeasurementScanner(tmpdir)
        print('----- first scan -----')
        time.sleep(0.5)
        scanner.scan_and_sync(repo)

        time.sleep(0.5)
        print('----- add files & scan again -----')
        (p / 'm002' / 'sample5.csv').touch()
        (p / 'm003').mkdir()
        (p / 'm003' / 'sample6.csv').touch()

        os.stat(p / 'm002')
        os.stat(p / 'm003')

        time.sleep(0.5)
        scanner.scan_and_sync(repo)

        buf = io.StringIO()
        scanner.save_cache(buf)
        buf.seek(0)
        scanner.load_cache(buf)

        print('----- results -----')
        pprint(repo.stats())
        pprint(scanner._cache)
