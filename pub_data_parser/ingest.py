"""Functions for ingesting and processing publication CSV files."""

from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List

import pandas as pd


def load_single_csv(csv_file: Path) -> pd.DataFrame:
    """
    Load a single CSV file into a pandas DataFrame.

    Parameters
    ----------
    csv_file : Path
        Path to CSV file

    Returns
    -------
    pd.DataFrame
        DataFrame containing the CSV data
    """
    return pd.read_csv(csv_file)


def load_csv_files(data_dir: str = "./data") -> List[pd.DataFrame]:
    """
    Load all CSV files from the specified directory into pandas DataFrames.

    Parameters
    ----------
    data_dir : str, optional
        Path to directory containing CSV files, by default "./data"
    workers : int, optional
        Number of worker processes to use, by default 4

    Returns
    -------
    List[pd.DataFrame]
        List of pandas DataFrames, one for each CSV file
    """
    data_path = Path(data_dir)
    csv_files = list(data_path.glob("*.csv"))

    # Use min of available CPUs, requested workers, and number of files
    n_workers = min(cpu_count(), len(csv_files))

    with Pool(n_workers) as pool:
        dataframes = pool.map(load_single_csv, csv_files)

    return dataframes


def extract_pmids(dataframes: List[pd.DataFrame]) -> List[int]:
    """
    Extract PMIDs from a list of DataFrames and return as integers.

    Parameters
    ----------
    dataframes : List[pd.DataFrame]
        List of pandas DataFrames containing publication data

    Returns
    -------
    List[int]
        List of unique PMIDs as integers
    """
    all_pmids = []

    for df in dataframes:
        # Look for common PMID column names
        pmid_cols = [col for col in df.columns if "pmid" in col.lower()]

        if pmid_cols:
            # Use the first found PMID column
            pmids = df[pmid_cols[0]].dropna().astype(int).tolist()
            all_pmids.extend(pmids)

    # Remove duplicates and sort
    return sorted(list(set(all_pmids)))


def get_all_pmids(data_dir: str = "./data", workers: int = 4) -> List[int]:
    """
    Load CSV files and extract all unique PMIDs.

    Parameters
    ----------
    data_dir : str, optional
        Path to directory containing CSV files, by default "./data"
    workers : int, optional
        Number of worker processes to use, by default 4

    Returns
    -------
    List[int]
        List of unique PMIDs as integers
    """
    dataframes = load_csv_files(data_dir)
    return extract_pmids(dataframes)
