# Pub-Data-Parser

A Python package for processing NIH RePORTER publication data, downloading Open Access PDFs, and identifying HHS Public Access versions.

## Introduction

Pub-Data-Parser is designed to streamline the process of:

- Aggregating CSV files from NIH RePORTER
- Extracting PMIDs from publication data
- Downloading Open Access publications using Metapub
- Separating HHS Public Access PDFs from publisher versions

The package handles parallel processing for efficient PDF downloads and analysis, with built-in rate limiting for NCBI API requests.

## Installation

```bash
pip install -e .
```

## Environment Setup

The package uses python-dotenv to manage the NCBI API key. Create a `.env` file in your project root:

```bash
touch .env
```

Add your NCBI API key to the `.env` file:

```
NCBI_API_KEY=your_api_key_here
```

To obtain an NCBI API key:

1. Create an NCBI account at <https://www.ncbi.nlm.nih.gov/>
2. Go to your account settings
3. Navigate to the API Key Management section
4. Generate a new API key

Note: Without an API key, the package will limit requests to 3 per second. With an API key, this increases to 10 requests per second.

## Usage

The main workflow is implemented in `main.py`, which demonstrates the full pipeline:

```python
from pathlib import Path
from pub_data_parser import (
    get_all_pmids,
    get_urls_from_pmids,
    download_pdfs_from_csv,
    validate_pdfs,
    segregate_pdfs,
    process_pdfs_parallel,
    segregate_hhs
)

# Get PMIDs from CSV files in ./data directory
pmids = get_all_pmids()

# Get URLs for PMIDs
get_urls_from_pmids(pmids, output_file="article_urls.csv")

# Download PDFs
download_pdfs_from_csv(input_file="article_urls.csv")

# Validate and process PDFs
validation = validate_pdfs(directory=Path("pdfs"))
segregate_pdfs(validation)
process_pdfs_parallel(directory=Path("pdfs"), output_csv=Path("hhs_info.csv"))
segregate_hhs(csv_path=Path("hhs_info.csv"))
```

### Function Explanations

- `get_all_pmids()`: Reads CSV files from the `./data` directory and extracts unique PMIDs
- `get_urls_from_pmids()`: Uses Metapub to find download URLs for each PMID
- `download_pdfs_from_csv()`: Downloads PDFs from the URLs in parallel
- `validate_pdfs()`: Checks if downloaded files are valid PDFs
- `segregate_pdfs()`: Moves invalid PDFs to an 'invalid' subdirectory
- `process_pdfs_parallel()`: Analyzes PDFs for HHS Public Access markers
- `segregate_hhs()`: Separates PDFs into 'hhs' and 'unknown' subdirectories based on analysis

## Output Structure

After running the pipeline, files will be organized as follows:

```text
project/
├── pdfs/
│   ├── hhs/         # HHS Public Access PDFs
│   ├── unknown/     # PDFs with unclear status
│   └── invalid/     # Invalid or corrupted PDFs
├── article_urls.csv  # URLs for each PMID
├── hhs_info.csv     # Analysis results
└── download.log     # Download process log
```

## License

CC0 1.0 Universal
