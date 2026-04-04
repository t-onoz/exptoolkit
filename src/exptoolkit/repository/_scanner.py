from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict

from exptoolkit.repository._repo import ResourceRepo, MID

class ScanResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    ref: str
    measurement_id: MID
    samples: str | tuple[str, ...]
    data_type: str | None = None


class ResourceScanner(ABC):
    """
    Scan external resources and sync them to a ResourceRepo.

    Each scanner owns a subset of refs.
    `scan()` must return ALL resources in that subset.
    """

    @abstractmethod
    def owns(self, ref: str) -> bool:
        """
        Return True if this scanner is responsible for the ref.
        """
        ...

    @abstractmethod
    def scan(self) -> list[ScanResult]:
        """
        Return a complete list of resources owned by this scanner.

        Rules:
            - All refs must satisfy owns(ref) == True
            - Must be complete (no missing refs)
        """
        ...

    def scan_and_sync(self, repo: ResourceRepo) -> None:
        """
        Sync repo with current scan result.

        - Add new resources
        - Remove missing resources (only owned refs)
        """
        results = self.scan()
        new_refs = {r.ref: r for r in results}

        # add or update
        for r in results:
            repo.add(
                r.ref,
                measurement_id=r.measurement_id,
                samples=r.samples,
                data_type=r.data_type,
            )

        # remove (owned only)
        for ref in list(repo._ref2d.keys()):
            if self.owns(ref) and ref not in new_refs:
                repo.remove(ref)
