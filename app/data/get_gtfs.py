import os
import io
import zipfile
import requests
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
DATABASE_URL = os.getenv("DATABASE_URL", None)

GTFS_URL = "http://www.ridepatco.org/developers/PortAuthorityTransitCorporation.zip"
GTFS_DATA_DIR = Path("./app/data/gtfs_csvs")


def download_and_extract_gtfs_zip(url: str = GTFS_URL, data_dir: Path = GTFS_DATA_DIR):
    """Download and extract the GTFS zip file"""
    if not data_dir.exists():
        data_dir.mkdir()

    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path=data_dir)


def import_single_csv_to_postgres(data_path: Path):
    """Import a single CSV file to Postgres"""
    print(data_path)
    df = pd.read_csv(data_path)
    df.to_sql(
        data_path.stem,
        con=create_engine(DATABASE_URL),
        if_exists="replace",
    )


def import_all_csvs_to_posgres():
    """Add all text files from the zip package to Postgres"""
    download_and_extract_gtfs_zip()

    for csv_path in GTFS_DATA_DIR.rglob("*.txt"):
        import_single_csv_to_postgres(csv_path)


if __name__ == "__main__":
    import_all_csvs_to_posgres()
