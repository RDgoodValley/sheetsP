import gspread
import os
from google.oauth2.service_account import Credentials

# Zakres uprawnień
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Ścieżka do pliku credentials.json (pobierz z Google Cloud Console)
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Funkcja do ekstrakcji ID arkusza z pełnego URL
def extract_sheet_id(sheet_id_or_url):
    """Ekstrahuje ID arkusza z pełnego URL lub zwraca ID, jeśli już jest ID."""
    if 'docs.google.com/spreadsheets/d/' in sheet_id_or_url:
        # Ekstrahuj ID z URL
        return sheet_id_or_url.split('/d/')[1].split('/')[0]
    return sheet_id_or_url

# Funkcja do autoryzacji
def authenticate_google_sheets():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Plik {SERVICE_ACCOUNT_FILE} nie istnieje.\n"
            "Kroki:\n"
            "1. Przejdź do Google Cloud Console (https://console.cloud.google.com/)\n"
            "2. Utwórz konto usługi i pobierz klucz JSON\n"
            "3. Umieść plik credentials.json w tym katalogu"
        )
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

# Funkcja do czytania danych z arkusza
def read_data(sheet_id, sheet_name='Sheet1', use_raw_data=False):
    sheet_id = extract_sheet_id(sheet_id)  # Ekstrahuj ID, jeśli podano URL
    client = authenticate_google_sheets()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    
    try:
        # Próbuj czytać jako dict (z nagłówkami)
        data = sheet.get_all_records()
    except Exception as e:
        if "duplicates" in str(e):
            # Jeśli są duplikaty w nagłówkach, czytaj jako surowe dane
            print("⚠️  Arkusz ma duplikaty w nagłówkach. Czytam jako surowe dane...")
            data = sheet.get_all_values()
        else:
            raise
    
    return data

# Funkcja do zapisywania danych do arkusza
def write_data(sheet_id, data, sheet_name='Sheet1'):
    sheet_id = extract_sheet_id(sheet_id)  # Ekstrahuj ID, jeśli podano URL
    client = authenticate_google_sheets()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    sheet.append_row(data)
    print(f"✓ Dane zapisane: {data}")

# Przykład użycia
if __name__ == "__main__":
    # Zastąp przy użyciu pełnego URL lub samego ID arkusza Google Sheets
    SHEET_ID = 'https://docs.google.com/spreadsheets/d/1O5djKeS5IxF0pKBIjjwF_atC6N_2JPdXqUEtTY4cmSg/edit?gid=0#gid=0'
    # Alternatywnie możesz użyć pełnego URL:
    # SHEET_ID = 'https://docs.google.com/spreadsheets/d/YOUR_ID/edit'

    try:
        # Czytanie danych
        print("📖 Czytanie danych...")
        data = read_data(SHEET_ID)
        print(f"✓ Przeczytano {len(data)} wierszy:")
        for i, row in enumerate(data[:5], 1):  # Pokaż pierwszy 5 wierszy
            print(f"  {i}. {row}")
        if len(data) > 5:
            print(f"  ... i {len(data) - 5} więcej wierszy")

        # Zapisywanie danych
        print("\n📝 Zapisywanie danych...")
        write_data(SHEET_ID, ['Przykład', 'Danych', '123'])
        
    except FileNotFoundError as e:
        print(f"❌ Błąd: {e}")
        print("\nAby naprawić ten problém:\n")
        print("1. Utwórz projekt w https://console.cloud.google.com/")
        print("2. Włącz Google Sheets API")
        print("3. Utwórz Service Account i pobierz klucz JSON")
        print("4. Umieść plik credentials.json w tym katalogu")
        print("5. Udostępnij arkusz e-mail z pliku credentials.json")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ Błąd: Arkusz o ID '{SHEET_ID}' nie znaleziony.")
        print("Upewnij się, że:\n")
        print("- ID arkusza jest prawidłowy")
        print("- Arkusz jest udostępniony dla konta usługi")
        print("- API jest włączone")
    except Exception as e:
        print(f"❌ Błąd: {e}")
