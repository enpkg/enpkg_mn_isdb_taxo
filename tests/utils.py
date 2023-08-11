"""Utilities for the unit tests."""

from downloaders import BaseDownloader


def retrieve_zenodo_data():
    """Retrieve the data from Zenodo."""
    downloader = BaseDownloader()
    downloader.download(
        "https://zenodo.org/record/8225411/files/enpkg_taxo_enhancer_output.tar.gz?download=1",
        "./tests/data/enpkg_taxo_enhancer_output.tar.gz",
    )
    downloader.download(
        "https://zenodo.org/record/7534071/files/230106_frozen_metadata.csv.gz",
        "./db_metadata/230106_frozen_metadata.csv.gz",
    )
    downloader.download(
        "https://zenodo.org/record/7534250/files/isdb_pos.mgf",
        "./db_spectra/isdb_pos.mgf",
    )
    