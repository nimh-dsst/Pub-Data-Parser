"""
pub-data-parser - A package for parsing publications for data
deposition statements
"""

import dotenv

from .download import download_pdfs_from_csv
from .ingest import get_all_pmids
from .url import get_urls_from_pmids
from .verify import (
    validate_pdfs,
    segregate_pdfs,
    process_pdfs_parallel,
    segregate_hhs,
)

__version__ = "0.1.0"
__author__ = "Josh Lawrimore"
__license__ = "CC0 1.0 Universal"

# Load environment variables
dotenv.load_dotenv()

# Define public API
__all__ = [
    "download_pdfs_from_csv",
    "get_all_pmids",
    "get_urls_from_pmids",
    "validate_pdfs",
    "segregate_pdfs",
    "process_pdfs_parallel",
    "segregate_hhs",
]
