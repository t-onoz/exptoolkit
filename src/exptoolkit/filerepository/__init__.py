"""Classes for indexing and searching measurement files stored on a root folder.
Provides `MeasurementRepo`, an in-memory index supporting lookup by request,
sample name, and measurement ID. Measurements are organized relative to a
root directory, and file locations are represented by paths relative to that
root.

This subpackage is independent of others.
"""
from exptoolkit.filerepository._datarepo import (
    MeasurementRepo,
    Measurement,
    DataFile,
)
