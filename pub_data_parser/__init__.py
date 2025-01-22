"""
pub-data-parser - A package for parsing publications for data
deposition statements
"""

import dotenv

# Load environment variables
dotenv.load_dotenv()

from .download import download_pdfs_from_csv  # noqa: E402
from .ingest import get_all_pmids  # noqa: E402
from .url import get_urls_from_pmids  # noqa: E402
from .verify import (  # noqa: E402
    process_pdfs_parallel,
    segregate_hhs,
    segregate_pdfs,
    validate_pdfs,
)

__version__ = "0.1.0"
__author__ = "Josh Lawrimore"
__license__ = "CC0 1.0 Universal"

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
