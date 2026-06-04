from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from pathlib import Path
import io

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CREDENTIALS_FILE = BASE_DIR / "src" / "data" / "service_account.json"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "datos.csv"
FILE_ID = "TU_FILE_ID_DEL_CSV_EN_DRIVE"

def descargar_csv():
    creds = service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_FILE),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=FILE_ID)
    with io.FileIO(str(OUTPUT_PATH), "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print(f"✅ CSV descargado en {OUTPUT_PATH}")

if __name__ == "__main__":
    descargar_csv()