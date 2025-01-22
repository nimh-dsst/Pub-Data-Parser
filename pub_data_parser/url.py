"""Functions for retrieving article URLs using metapub."""

import asyncio
import csv
import os
from pathlib import Path
from typing import Any, Dict, List

from metapub import FindIt  # type: ignore


def get_rate_limit() -> float:
    """
    Get rate limit based on NCBI API key presence.

    Returns
    -------
    float
        Time in seconds to wait between requests (0.1 with key, 0.33 without)
    """
    return 0.1 if os.getenv("NCBI_API_KEY") else 0.33


async def get_article_info(pmid: int, timeout: int = 5) -> Dict[str, Any]:
    """
    Asynchronously retrieve article information for a single PMID.

    Parameters
    ----------
    pmid : int
        PubMed ID to look up
    timeout : int, optional
        Timeout in seconds, by default 5

    Returns
    -------
    Dict[str, Any]
        Dictionary containing article information
    """
    try:
        async with asyncio.timeout(timeout):
            # Apply rate limiting
            await asyncio.sleep(get_rate_limit())
            finder = FindIt(pmid)
            return {
                "pmid": pmid,
                "url": finder.url,
                "backup_url": finder.backup_url,
                "reason": finder.reason,
                "title": finder.pma.title if finder.pma else None,
            }
    except asyncio.TimeoutError:
        return {
            "pmid": pmid,
            "url": None,
            "backup_url": None,
            "reason": "Timeout",
            "title": None,
        }
    except Exception as e:
        return {
            "pmid": pmid,
            "url": None,
            "backup_url": None,
            "reason": str(e),
            "title": None,
        }


async def write_chunk_results(
    results: List[Dict[str, Any]], writer: csv.DictWriter
) -> None:
    """
    Write chunk results to CSV file.

    Parameters
    ----------
    results : List[Dict[str, Any]]
        List of article information dictionaries
    writer : csv.DictWriter
        CSV writer object
    """
    for result in results:
        writer.writerow(result)


async def process_pmids(
    pmids: List[int], output_file: str, chunk_size: int = 5
) -> None:
    """
    Process PMIDs in chunks using asyncio and write results to CSV.

    Parameters
    ----------
    pmids : List[int]
        List of PMIDs to process
    output_file : str
        Path to output CSV file
    chunk_size : int, optional
        Number of PMIDs to process in each chunk, by default 5
    """
    fieldnames = ["pmid", "url", "backup_url", "reason", "title"]
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Process PMIDs in chunks
        for i in range(0, len(pmids), chunk_size):
            chunk = pmids[i : i + chunk_size]
            tasks = [get_article_info(pmid) for pmid in chunk]
            chunk_results = await asyncio.gather(*tasks)
            await write_chunk_results(chunk_results, writer)


def get_urls_from_pmids(
    pmids: List[int],
    output_file: str = "article_urls.csv",
    chunk_size: int = 5,
) -> None:
    """
    Main function to get URLs from a list of PMIDs and write to CSV.

    Parameters
    ----------
    pmids : List[int]
        List of PMIDs to process
    output_file : str, optional
        Path to output CSV file, by default "article_urls.csv"
    chunk_size : int, optional
        Number of PMIDs to process in each chunk, by default 5
    """
    asyncio.run(process_pmids(pmids, output_file, chunk_size))
