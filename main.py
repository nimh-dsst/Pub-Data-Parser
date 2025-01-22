from pathlib import Path

from pub_data_parser import (
    download_pdfs_from_csv,
    get_all_pmids,
    get_urls_from_pmids,
    process_pdfs_parallel,
    segregate_hhs,
    segregate_pdfs,
    validate_pdfs,
)

if __name__ == "__main__":
    pmids: list[int] = get_all_pmids()
    pmids = pmids
    get_urls_from_pmids(pmids, output_file="article_urls.csv")
    download_pdfs_from_csv(input_file="article_urls.csv", num_processes=1)
    validation: dict = validate_pdfs(directory=Path("pdfs"), num_processes=1)
    segregate_pdfs(validation)
    process_pdfs_parallel(
        directory=Path("pdfs"),
        output_csv=Path("hhs_info.csv"),
        num_processes=1,
    )
    segregate_hhs(csv_path=Path("hhs_info.csv"))
