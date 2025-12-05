import pandas as pd
from datetime import datetime
import os, io, re, glob, json, yaml
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

# ----------------------
# Load Config
# ----------------------
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# ----------------------
# Constants & Setup
# ----------------------
DATA_BASE_DIR = config["paths"]["data_base_dir"]
USER_DATA_DIR = config["paths"]["user_data_dir"]
ACCOUNTS_LIST = config["paths"]["accounts_list"]
CATEGORY_LIST = config["paths"]["categories_file"]

DRIVE_FOLDER_ID = config["google_drive"]["folder_id"]
SCOPES = config["google_drive"]["scopes"]

DEFAULT_CATEGORIES = config["defaults"]["categories"]

columns = ['Transaction ID', 'Date', 'Amount', 'Category', 'Description', 'Balance']
account_name = None
piggy_bank = None
loaded_year = None
transactions_df = pd.DataFrame(columns=columns)
transaction_counter = 1
current_balance = 0.0

# ----------------------
# Account Management
# ----------------------
def load_accounts():
    if os.path.exists(ACCOUNTS_LIST):
        return json.load(open(ACCOUNTS_LIST, 'r', encoding='utf-8'))
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_LIST, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, ensure_ascii=False, indent=2)

def select_account():
    global account_name
    accounts = load_accounts()
    if accounts:
        print("已有帳戶：")
        for i, acc in enumerate(accounts, 1):
            print(f"{i}. {acc}")
        print(f"{len(accounts)+1}. ➕ 新增帳戶")
        choice = input(f"選擇帳戶 (1-{len(accounts)+1}): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(accounts):
                account_name = accounts[idx - 1]
                print(f"✅ 使用帳戶：{account_name}")
                return
    # 新增帳戶
    while True:
        acc = input("輸入新帳戶名稱: ").strip()
        if re.match(r"^[\w\-]+$", acc):
            if acc not in accounts:
                accounts.append(acc)
                save_accounts(accounts)
            account_name = acc
            print(f"✅ 使用帳戶：{account_name}")
            break
        else:
            print("❌ 無效名稱")

# ----------------------
# Piggy Bank Management
# ----------------------
def load_piggy_banks():
    base = os.path.join(USER_DATA_DIR, account_name, "piggy_banks")
    if not os.path.exists(base):
        return []
    return [name for name in os.listdir(base)
            if os.path.isdir(os.path.join(base, name))]

def save_piggy_bank(name):
    folder = os.path.join(USER_DATA_DIR, account_name, "piggy_banks", name)
    os.makedirs(folder, exist_ok=True)

def select_piggy_bank():
    global piggy_bank
    banks = load_piggy_banks()
    print("\n🐷 你的存錢筒：")
    for i, b in enumerate(banks, 1):
        print(f"{i}. {b}")
    print(f"{len(banks)+1}. ➕ 新增存錢筒")

    choice = input(f"選擇 (1-{len(banks)+1}): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(banks):
            piggy_bank = banks[idx-1]
            print(f"✅ 使用存錢筒：{piggy_bank}")
            return

    # Add new
    while True:
        new = input("請輸入新的存錢筒名稱: ").strip()
        if re.match(r"^[\w\-]+$", new):
            save_piggy_bank(new)
            piggy_bank = new
            print(f"🐷 已新增存錢筒: {piggy_bank}")
            return
        print("❌ 無效名稱")

# ----------------------
# File Path Helpers
# ----------------------
def get_piggy_bank_folder(extension='csv'):
    global account_name, piggy_bank
    folder = os.path.join(USER_DATA_DIR, account_name, "piggy_banks", piggy_bank, extension)
    os.makedirs(folder, exist_ok=True)
    return folder

def get_filename(year=None, extension='csv'):
    if year is None:
        year = datetime.now().year
    folder = get_piggy_bank_folder(extension)
    name = f"{year}_transactions.{extension}"
    return os.path.join(folder, name)

def list_transaction_files(extension='csv'):
    folder = get_piggy_bank_folder(extension)
    pattern = os.path.join(folder, f"*_transactions.{extension}")
    files = glob.glob(pattern)
    year_map = {}
    for f in files:
        name = os.path.basename(f)
        m = re.match(r"(\d{4})_transactions\." + extension + "$", name)
        if m:
            year_map[int(m.group(1))] = f
    return year_map

# ----------------------
# Category Handling
# ----------------------
def load_categories():
    if os.path.exists(CATEGORY_LIST):
        try:
            cats = json.load(open(CATEGORY_LIST, 'r', encoding='utf-8'))
            if not isinstance(cats, list): cats = []
        except:
            cats = []
    else:
        cats = []
    cats.sort()
    if not cats:
        cats = DEFAULT_CATEGORIES.copy()
        save_categories(cats)
    return cats

def save_categories(categories):
    with open(CATEGORY_LIST, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

def choose_category():
    cats = load_categories()
    print("\n請選擇分類：")
    for i, c in enumerate(cats, 1):
        print(f"{i}. {c}")
    print(f"{len(cats)+1}. 新增自訂分類")
    while True:
        choice = input(f"輸入選項 1–{len(cats)+1}: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(cats):
                return cats[idx - 1]
            if idx == len(cats) + 1:
                new = input("輸入新的分類名稱: ").strip()
                if new and new not in cats:
                    cats.append(new)
                    save_categories(cats)
                    print(f"✅ 已新增分類: {new}")
                    return new
        print("❌ 無效選項")

# ----------------------
# Utilities
# ----------------------
def refresh_balance():
    global transactions_df, transaction_counter, current_balance
    if transactions_df.empty:
        print("⚠️ 沒有交易紀錄可刷新。")
        return
    transactions_df.sort_values(by=['Date', 'Transaction ID'], inplace=True, ignore_index=True)
    bal = 0
    balances = []
    for amt in transactions_df['Amount']:
        bal += amt
        balances.append(bal)
    transactions_df['Balance'] = balances
    transaction_counter = transactions_df['Transaction ID'].max() + 1
    current_balance = balances[-1]
    print("🔄 餘額已重新計算完畢。")

# ----------------------
# Transaction Recording & Removal
# ----------------------
def record_transaction(date, amount, category, description):
    global transaction_counter, transactions_df, current_balance
    date = pd.to_datetime(date)
    balance = current_balance + amount
    transactions_df.loc[len(transactions_df)] = {
        'Transaction ID': transaction_counter,
        'Date': date,
        'Amount': amount,
        'Category': category,
        'Description': description,
        'Balance': balance
    }
    current_balance = balance
    transaction_counter += 1
    refresh_balance()
    print(f"✅ 交易已記錄: {amount:.2f} | {category} | {description}")

def remove_transaction_by_date():
    global transactions_df, transaction_counter, current_balance
    date_str = input("輸入要刪除的日期 (YYYY-MM-DD): ").strip()
    try:
        td = pd.to_datetime(date_str).normalize()
    except:
        print("❌ 日期格式錯誤。")
        return
    df_day = transactions_df[transactions_df['Date'].dt.normalize() == td]
    if df_day.empty:
        print(f"⚠️ 該日期無交易：{date_str}")
        return
    print(f"\n{date_str} 的交易：")
    for i, (_, r) in enumerate(df_day.iterrows(), 1):
        print(f"{i}. ID:{r['Transaction ID']}  金額:{r['Amount']}  分類:{r['Category']}  描述:{r['Description']}")
    choice = input("輸入要刪除編號 (0 取消): ").strip()
    if choice == '0':
        print("取消刪除。")
        return
    try:
        i = int(choice) - 1
        idx = df_day.index[i]
    except:
        print("❌ 無效選項。")
        return
    removed = transactions_df.loc[idx]
    transactions_df = transactions_df.drop(idx).reset_index(drop=True)
    transactions_df['Transaction ID'] = range(1, len(transactions_df) + 1)
    bal = 0
    balances = []
    for amt in transactions_df['Amount']:
        bal += amt
        balances.append(bal)
    transactions_df['Balance'] = balances
    transaction_counter = len(transactions_df) + 1
    current_balance = balances[-1] if balances else 0.0
    refresh_balance()
    print(f"✅ 已刪除: ID {removed['Transaction ID']} 金額:{removed['Amount']} 分類:{removed['Category']}")

# ----------------------
# Reporting
# ----------------------
def summarize_expense_by_category(df):
    filtered = df[(df['Amount'] < 0) & (df['Category'].str.lower() != 'savings')]
    total = filtered['Amount'].sum()
    for cat, amt in filtered.groupby('Category')['Amount'].sum().sort_values().items():
        print(f"- {cat}: {amt:.2f} ({amt/total*100:.1f}%)")

def generate_monthly_report(year, month):
    start = datetime(year, month, 1)
    end = datetime(year, month+1, 1) if month < 12 else datetime(year+1, 1, 1)
    mdf = transactions_df[(transactions_df['Date'] >= start) & (transactions_df['Date'] < end)]
    balance_before = transactions_df[transactions_df['Date'] < start]['Amount'].sum()
    inc = mdf[mdf['Amount'] > 0]['Amount'].sum()
    exp = mdf[mdf['Amount'] < 0]['Amount'].sum()
    net = inc + exp
    print(f"\n--- {year}-{month:02d} 月報 ---")
    print(f"期初: {balance_before:.2f}  收入: {inc:.2f}  支出: {exp:.2f}  淨額: {net:.2f}  期末: {balance_before+net:.2f}")
    if not mdf.empty:
        print("\n🔻 支出分類：")
        summarize_expense_by_category(mdf)
        print("\n🔺 收入分類：")
        for cat, amt in mdf[mdf['Amount'] > 0].groupby('Category')['Amount'].sum().sort_values(ascending=False).items():
            print(f"- {cat}: {amt:.2f} ({amt/inc*100:.1f}%)")

def generate_yearly_report(year):
    start = datetime(year, 1, 1)
    end = datetime(year+1, 1, 1)
    ydf = transactions_df[(transactions_df['Date'] >= start) & (transactions_df['Date'] < end)]
    balance_before = transactions_df[transactions_df['Date'] < start]['Amount'].sum()
    inc = ydf[ydf['Amount']>0]['Amount'].sum()
    exp = ydf[ydf['Amount']<0]['Amount'].sum()
    net = inc + exp
    print(f"\n=== {year} 年報 ===")
    print(f"年初: {balance_before:.2f}  收入: {inc:.2f}  支出: {exp:.2f}  淨額: {net:.2f}  年末: {balance_before+net:.2f}")
    if not ydf.empty:
        print("\n🔻 支出分類：")
        for cat, amt in ydf[ydf['Amount']<0].groupby('Category')['Amount'].sum().sort_values().items():
            print(f"- {cat}: {amt:.2f} ({amt/exp*100:.1f}%)")
        print("\n🔺 收入分類：")
        for cat, amt in ydf[ydf['Amount']>0].groupby('Category')['Amount'].sum().sort_values(ascending=False).items():
            print(f"- {cat}: {amt:.2f} ({amt/inc*100:.1f}%)")

# ----------------------
# File I/O
# ----------------------
def load_from_csv(year=None):
    global transactions_df, transaction_counter, current_balance, loaded_year
    files = list_transaction_files('csv')
    if not files:
        print("⚠️ 沒有可用的 CSV 檔案。")
        return
    if year is None:
        year = max(files.keys())
    loaded_year = year
    fn = get_filename(year, 'csv')
    try:
        transactions_df = pd.read_csv(fn, parse_dates=['Date'])
    except FileNotFoundError:
        print(f"⚠️ 找不到 {fn}，從空白開始。")
        transactions_df = pd.DataFrame(columns=columns)
        current_balance = 0.0
        return
    if 'Balance' not in transactions_df:
        bal=0; balances=[]
        for amt in transactions_df['Amount']:
            bal+=amt; balances.append(bal)
        transactions_df['Balance'] = balances
    transactions_df.sort_values(by=['Date', 'Transaction ID'], inplace=True, ignore_index=True)
    transaction_counter = transactions_df['Transaction ID'].max()+1 if not transactions_df.empty else 1
    current_balance = transactions_df['Balance'].iloc[-1] if not transactions_df.empty else 0.0
    print(f"✅ 已載入 {fn}，共有 {len(transactions_df)} 筆")

def save_to_csv(year=None):
    global transactions_df
    transactions_df.sort_values(by=['Date', 'Transaction ID'], inplace=True, ignore_index=True)
    fn = get_filename(year, 'csv')
    transactions_df.to_csv(fn, index=False, encoding='utf-8-sig')
    print(f"📄 已儲存 CSV: {fn}")

# ----------------------
# Google Drive Integration
# ----------------------
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json','w') as f:
            f.write(creds.to_json())
    return creds

def upload_csv(service, file_path, file_name):
    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(file_path, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ 已上傳至指定資料夾，ID：{file.get('id')}")
    return file.get('id')

def download_csv_as_df(service, file_id):
    try:
        request = service.files().export_media(fileId=file_id, mimeType='text/csv')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        df = pd.read_csv(fh, parse_dates=['Date'])
        return df
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return pd.DataFrame(columns=columns)

# ----------------------
# CLI Menu
# ----------------------
def menu():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    while True:
        print(f"\n📘 選單： (帳戶: {account_name} | 存錢筒: {piggy_bank} | 目前年度: {loaded_year if loaded_year else '尚未載入'})")
        print("1. 新增交易")
        print("2. 刪除交易（按日期）")
        print("3. 月度報告")
        print("4. 年度報告")
        print("5. 儲存資料")
        print("6. 載入資料")
        print("7. 上傳至 Google Drive")
        print("8. 下載 CSV 從 Drive")
        print("9. 更換存錢筒（Piggy Bank）")
        print("10. 離開")

        choice = input("請輸入選項 (1-10): ").strip()

        if choice == '1':
            date = input("日期 (YYYY-MM-DD): ")
            amt = float(input("金額 (收入正／支出負): "))
            cat = choose_category()
            desc = input("描述: ")
            record_transaction(date, amt, cat, desc)

        elif choice == '2':
            remove_transaction_by_date()

        elif choice == '3':
            y = int(input("年份(YYYY): "))
            m = int(input("月份(1-12): "))
            generate_monthly_report(y, m)

        elif choice == '4':
            y = int(input("年份(YYYY): "))
            generate_yearly_report(y)

        elif choice == '5':
            save_to_csv()

        elif choice == '6':
            y = input("年份(留空使用最新): ").strip()
            load_from_csv(int(y) if y else None)

        elif choice == '7':
            fn = get_filename(loaded_year if loaded_year else None, 'csv')
            upload_csv(service, fn, os.path.basename(fn))

        elif choice == '8':
            file_id = input("輸入 Google Drive 檔案 ID: ")
            df = download_csv_as_df(service, file_id)
            if not df.empty:
                global transactions_df
                transactions_df = df
                refresh_balance()
                print("✅ 已載入 Drive CSV")

        elif choice == '9':
            select_piggy_bank()
            load_from_csv()

        elif choice == '10':
            print("👋 再見！")
            break


        else:
            print("❌ 無效選項。")

# ----------------------
# Startup
# ----------------------
if __name__ == "__main__":
    select_account()
    select_piggy_bank()
    load_from_csv()
    menu()
