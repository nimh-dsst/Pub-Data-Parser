"""Functions for downloading PDFs from article URLs."""

import csv
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Tuple

import requests


def setup_logging() -> None:
    """Configure logging for the download process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    # Add file handler for download.log
    file_handler = logging.FileHandler("download.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.getLogger().addHandler(file_handler)


def check_if_pdf(response: requests.Response) -> bool:
    """
    Check if response content is a PDF.

    Parameters
    ----------
    response : requests.Response
        Response from URL request

    Returns
    -------
    bool
        True if content appears to be PDF, False otherwise
    """
    # Check content type header
    if "application/pdf" in response.headers.get("content-type", "").lower():
        return True

    # Check file signature (PDF magic number)
    return response.content.startswith(b"%PDF-")


def download_pdf(
    url: str, pmid: int, pdf_dir: str = "./pdfs"
) -> Tuple[int, str, bool]:
    """
    Download PDF from URL and save to file.

    Parameters
    ----------
    url : str
        URL to download PDF from
    pmid : int
        PMID of the article
    pdf_dir : str, optional
        Directory to save PDFs, by default "./pdfs"

    Returns
    -------
    Tuple[int, str, bool]
        PMID, status message, and success flag
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if check_if_pdf(response):
            pdf_path = Path(pdf_dir) / f"{pmid}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)

            with open(pdf_path, "wb") as f:
                f.write(response.content)
            return pmid, "Success", True

        return pmid, "Not a PDF", False

    except requests.RequestException as e:
        return pmid, f"Download failed: {str(e)}", False


def process_url_batch(
    urls: List[Tuple[int, str | None]]
) -> List[Tuple[int, str, bool]]:
    """
    Process a batch of URLs for PDF download.

    Parameters
    ----------
    urls : List[Tuple[int, str | None]]
        List of (PMID, URL) tuples to process

    Returns
    -------
    List[Tuple[int, str, bool]]
        List of (PMID, status, success) tuples
    """
    results = []
    for pmid, url in urls:
        if url:  # Only process if URL exists
            result = download_pdf(url, pmid)
        else:
            result = (pmid, "No URL available", False)
        results.append(result)
    return results


def write_inventory(
    results: List[Tuple[int, str, bool]], timestamp: str
) -> None:
    """
    Write PDF download results to inventory CSV.

    Parameters
    ----------
    results : List[Tuple[int, str, bool]]
        List of download results
    timestamp : str
        Timestamp for inventory filename
    """
    filename = f"pdf_inventory_{timestamp}.csv"
    fieldnames = ["pmid", "status", "success"]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for pmid, status, success in results:
            writer.writerow(
                {"pmid": pmid, "status": status, "success": success}
            )


def download_pdfs_from_csv(input_file: str, batch_size: int = 10) -> None:
    """
    Download PDFs from URLs in CSV file using parallel processing.

    Parameters
    ----------
    input_file : str
        Path to input CSV file containing PMIDs and URLs
    batch_size : int, optional
        Size of URL batches for processing, by default 10
    """
    setup_logging()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    n_workers = cpu_count()

    logging.info(f"Starting PDF downloads with {n_workers} workers")

    # Read URLs from CSV
    url_batches: List[List[Tuple[int, str | None]]] = []
    current_batch: List[Tuple[int, str | None]] = []

    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pmid: int = int(row["pmid"])
            url: str | None = row.get("url")
            current_batch.append((pmid, url))

            if len(current_batch) >= batch_size:
                url_batches.append(current_batch)
                current_batch = []

    if len(current_batch) > 0:  # Add any remaining URLs
        url_batches.append(current_batch)

    # Process batches in parallel
    all_results = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        future_to_batch = {
            executor.submit(process_url_batch, batch): batch
            for batch in url_batches
        }

        for future in as_completed(future_to_batch):
            try:
                results = future.result()
                all_results.extend(results)
                logging.info(f"Completed batch of {len(results)} downloads")
            except Exception as e:
                logging.error(f"Batch processing failed: {str(e)}")

    # Write inventory
    write_inventory(all_results, timestamp)
    logging.info("Download process completed")
