import logging
import sys
import io
import time
import os
from pathlib import Path
from pprint import pprint
from tempfile import TemporaryDirectory

from exptoolkit.repository import DirectoryScanner, ResourceRepo

logging.basicConfig(stream=sys.stdout)
logging.getLogger('exptoolkit').setLevel(logging.DEBUG)

with TemporaryDirectory() as tmpdir:
    repo = ResourceRepo()
    p = Path(tmpdir)
    (p / 'm001').mkdir()
    (p / 'm002').mkdir()
    (p / 'failure').mkdir()
    (p / 'm001' / 'sample1.csv').touch()
    (p / 'm001' / 'sample2.csv').touch()
    (p / 'm002' / 'sample3.csv').touch()
    (p / 'm002' / 'sample4.csv').touch()
    (p / 'm002' / 'garbage.info').touch()
    (p / 'failure' / 'sample0.csv').touch()

    # This seems to refresh modification time of folders
    os.stat(p / 'm001')
    os.stat(p / 'm002')

    scanner = DirectoryScanner(tmpdir, dir_regex='m.*', file_regex='.*.csv', f_type=lambda e: 'csv')
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
    print(*(repr(dr) for dr in repo.iter_resources()), sep='\n')
    pprint(scanner._cache)
