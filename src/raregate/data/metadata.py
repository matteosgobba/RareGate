"""Pinned source metadata, cross-checked against Zenodo on 2026-10-04."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetSource:
    """Identity and publisher integrity information for the raw artifact."""

    dataset: str
    version: str
    record_id: int
    doi: str
    filename: str
    url: str
    expected_size: int
    expected_checksum: str
    checksum_algorithm: str = "md5"
    license: str = "CC-BY-4.0"


LHCO_RD = DatasetSource(
    dataset="LHC Olympics 2020 R&D",
    version="v5",
    record_id=6466204,
    doi="10.5281/zenodo.6466204",
    filename="events_anomalydetection_v2.h5",
    url=(
        "https://zenodo.org/api/records/6466204/files/"
        "events_anomalydetection_v2.h5/content"
    ),
    expected_size=2_908_260_409,
    expected_checksum="629789d55813be3860781b084ae7f1de",
)
