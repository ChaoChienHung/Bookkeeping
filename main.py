import os
import io
import re
import glob
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

def get_year_filename(year=None, extension='csv'):
    if year is None:
        year = datetime.now().year
    return f"{year}_transactions.{extension}"

# 授權範圍 (只讀寫Google Drive檔案)
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ========== Google Drive 驗證 ==========
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
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_csv(service, file_path, file_name):
    file_metadata = {'name': file_name, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    media = MediaFileUpload(file_path, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'✅ 已上傳檔案，ID：{file.get("id")}')
    return file.get('id')

def download_csv_as_df(service, file_id):
    request = service.files().export_media(fileId=file_id, mimeType='text/csv')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    df = pd.read_csv(fh)
    print(f'✅ 下載並讀取 CSV，行數：{len(df)}')
    return df

# ========== 金融紀錄系統 ==========
columns = ['Transaction ID', 'Date', 'Amount', 'Category', 'Description', 'Balance']
transactions_df = pd.DataFrame(columns=columns)
transaction_counter = 1
current_balance = 0.0

def record_transaction(date, amount, category, description):
    global transaction_counter, transactions_df, current_balance
    transaction = {
        'Transaction ID': transaction_counter,
        'Date': pd.to_datetime(date),
        'Amount': amount,
        'Category': category,
        'Description': description,
        'Balance': current_balance + amount
    }
    current_balance += amount
    transactions_df.loc[len(transactions_df)] = transaction
    transaction_counter += 1
    print(f"✅ 交易已記錄: {transaction}\n")


def generate_monthly_report(year, month):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    monthly_transactions = transactions_df[(transactions_df['Date'] >= start_date) & (transactions_df['Date'] < end_date)]

    balance_before = transactions_df[transactions_df['Date'] < start_date]['Amount'].sum()
    total_income = monthly_transactions[monthly_transactions['Amount'] > 0]['Amount'].sum()
    total_expenses = monthly_transactions[monthly_transactions['Amount'] < 0]['Amount'].sum()
    balance = total_income + total_expenses

    print(f"\n--- {year}-{month:02d} 月度報告 ---")
    print(f"📌 期初結餘: {balance_before:.2f} 元")
    print(f"📈 總收入: {total_income:.2f} 元")
    print(f"📉 總支出: {total_expenses:.2f} 元")
    print(f"💰 月結餘: {balance:.2f} 元")
    print(f"💼 期末結餘: {balance_before + balance:.2f} 元")

    if not monthly_transactions.empty:
        print("\n📊 各分類支出：")
        expenses = monthly_transactions[monthly_transactions['Amount'] < 0]
        if not expenses.empty:
            category_expenses = expenses.groupby('Category')['Amount'].sum().sort_values()
            for category, amount in category_expenses.items():
                percent = (amount / total_expenses) * 100 if total_expenses != 0 else 0
                print(f"- {category}: {amount:.2f} 元 ({percent:.2f}%)")

        print("\n📊 各分類收入：")
        incomes = monthly_transactions[monthly_transactions['Amount'] > 0]
        if not incomes.empty:
            category_income = incomes.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            for category, amount in category_income.items():
                percent = (amount / total_income) * 100 if total_income != 0 else 0
                print(f"- {category}: {amount:.2f} 元 ({percent:.2f}%)")


def generate_yearly_report(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    yearly_transactions = transactions_df[(transactions_df['Date'] >= start_date) & (transactions_df['Date'] < end_date)]

    balance_before = transactions_df[transactions_df['Date'] < start_date]['Amount'].sum()
    total_income = yearly_transactions[yearly_transactions['Amount'] > 0]['Amount'].sum()
    total_expenses = yearly_transactions[yearly_transactions['Amount'] < 0]['Amount'].sum()
    balance = total_income + total_expenses

    print(f"\n=== {year} 年度報告 ===")
    print(f"📌 年初結餘: {balance_before:.2f} 元")
    print(f"📈 總收入: {total_income:.2f} 元")
    print(f"📉 總支出: {total_expenses:.2f} 元")
    print(f"💰 年結餘: {balance:.2f} 元")
    print(f"💼 年末結餘: {balance_before + balance:.2f} 元")

    if not yearly_transactions.empty:
        print("\n📊 各分類支出：")
        expenses = yearly_transactions[yearly_transactions['Amount'] < 0]
        if not expenses.empty:
            category_expenses = expenses.groupby('Category')['Amount'].sum().sort_values()
            for category, amount in category_expenses.items():
                percent = (amount / total_expenses) * 100 if total_expenses != 0 else 0
                print(f"- {category}: {amount:.2f} 元 ({percent:.2f}%)")

        print("\n📊 各分類收入：")
        incomes = yearly_transactions[yearly_transactions['Amount'] > 0]
        if not incomes.empty:
            category_income = incomes.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            for category, amount in category_income.items():
                percent = (amount / total_income) * 100 if total_income != 0 else 0
                print(f"- {category}: {amount:.2f} 元 ({percent:.2f}%)")

def list_transaction_files(extension='csv'):
    pattern = f"*_{extension}"
    files = glob.glob(f"*_{extension}")
    year_file_map = {}

    for f in files:
        # Extract year from filename e.g. 2023_transactions.csv
        match = re.match(r"(\d{4})_transactions\." + extension + "$", f)
        if match:
            year = int(match.group(1))
            year_file_map[year] = f

    return year_file_map

# ========== 本地檔案操作 ==========
def save_to_csv(year=None):
    filename = get_year_filename(year, 'csv')

    # Sort by Date
    transactions_df.sort_values(by='Date', inplace=True)

    transactions_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"📄 資料已儲存為 CSV 檔案: {filename}")

def save_to_excel(year=None):
    filename = get_year_filename(year, 'xlsx')

    # Sort by Date
    transactions_df.sort_values(by='Date', inplace=True)

    transactions_df.to_excel(filename, index=False)
    print(f"📊 資料已儲存為 Excel 檔案: {filename}")


def load_from_csv(year=None):
    global transactions_df, transaction_counter, current_balance
    filename = get_year_filename(year, 'csv')

    try:
        transactions_df = pd.read_csv(filename, parse_dates=['Date'])

        # Rebuild Balance if missing
        if 'Balance' not in transactions_df.columns:
            print("ℹ️ 偵測到舊格式資料，正在補上 Balance 欄位...")
            balance = 0.0
            balances = []
            for amount in transactions_df['Amount']:
                balance += amount
                balances.append(balance)
            transactions_df['Balance'] = balances

        transaction_counter = transactions_df['Transaction ID'].max() + 1
        current_balance = transactions_df['Balance'].iloc[-1] if not transactions_df.empty else 0.0
        print(f"✅ 成功從 {filename} 載入 {len(transactions_df)} 筆資料")
    except FileNotFoundError:
        print(f"⚠️ 找不到 {filename}，將從空白開始。")
        transactions_df = pd.DataFrame(columns=columns)
        current_balance = 0.0

def load_from_excel(year=None):
    global transactions_df, transaction_counter, current_balance
    filename = get_year_filename(year, 'xlsx')

    try:
        transactions_df = pd.read_excel(filename, parse_dates=['Date'])

        transactions_df.sort_values(by='Date', inplace=True)

        # Rebuild Balance if missing
        if 'Balance' not in transactions_df.columns:
            print("ℹ️ 偵測到舊格式資料，正在補上 Balance 欄位...")
            balance = 0.0
            balances = []
            for amount in transactions_df['Amount']:
                balance += amount
                balances.append(balance)
            transactions_df['Balance'] = balances

        transaction_counter = transactions_df['Transaction ID'].max() + 1
        current_balance = transactions_df['Balance'].iloc[-1] if not transactions_df.empty else 0.0
        print(f"✅ 成功從 Excel 載入 {len(transactions_df)} 筆資料")
    except FileNotFoundError:
        print(f"⚠️ 找不到 {filename}，將從空白開始。")
        transactions_df = pd.DataFrame(columns=columns)
        current_balance = 0.0


# ========== 主選單 ==========
def menu():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    while True:
        print("\n📘 選單：")
        print("1. 新增交易")
        print("2. 查看月度報告")
        print("3. 查看年度報告")
        print("4. 儲存資料 (CSV / Excel)")
        print("5. 載入資料 (CSV / Excel)")
        print("6. 上傳至 Google Drive")
        print("7. 從 Google Drive 下載 CSV")
        print("8. 離開")
        choice = input("請輸入選項 (1-8): ")

        if choice == '1':
            date = input("輸入日期 (YYYY-MM-DD): ")
            amount = float(input("輸入金額 (收入為正，支出為負): "))
            category = input("輸入分類 (如：Food, Salary, Transport): ")
            description = input("輸入描述: ")
            record_transaction(date, amount, category, description)

        elif choice == '2':
            year = int(input("輸入年份 (YYYY): "))
            month = int(input("輸入月份 (1-12): "))
            generate_monthly_report(year, month)

        elif choice == '3':
            year = int(input("輸入年份 (YYYY): "))
            generate_yearly_report(year)

        elif choice == '4':
            save_to_csv()
            save_to_excel()

        elif choice == '5':
            file_type = input("輸入檔案類型 (csv / excel): ").strip().lower()
            if file_type not in ['csv', 'excel']:
                print("❌ 不支援的檔案格式。")
                continue

            files_map = list_transaction_files('csv' if file_type == 'csv' else 'xlsx')
            if not files_map:
                print(f"⚠️ 找不到任何 {file_type.upper()} 格式的交易檔案。")
                continue

            print("可用的交易年份檔案：")
            sorted_years = sorted(files_map.keys())
            for idx, year in enumerate(sorted_years, 1):
                print(f"{idx}. {year} ({files_map[year]})")

            choice_input = input("請輸入要載入的檔案編號 (或輸入 0 取消): ").strip()
            if choice_input == '0':
                print("取消載入檔案。")
                continue

            try:
                choice_idx = int(choice_input)
                if 1 <= choice_idx <= len(sorted_years):
                    year_to_load = sorted_years[choice_idx - 1]
                    if file_type == 'csv':
                        load_from_csv(year_to_load)
                    else:
                        load_from_excel(year_to_load)
                else:
                    print("❌ 選項編號無效。")
            except ValueError:
                print("❌ 輸入格式錯誤，請輸入數字。")



        elif choice == '6':
            save_to_csv()  # 儲存最新本地 CSV
            filename = get_year_filename('csv')
            upload_csv(service, filename, f"MyTransactions_{datetime.now().year}")


        elif choice == '7':
            file_id = input("請輸入要下載的 Google Sheet 檔案ID: ").strip()
            df = download_csv_as_df(service, file_id)
            global transactions_df, transaction_counter
            transactions_df = df
            transaction_counter = transactions_df['Transaction ID'].max() + 1
            print(f"✅ 已更新本地資料，共 {len(transactions_df)} 筆交易")

        elif choice == '8':
            print("👋 程式結束，再見！")
            break

        else:
            print("❌ 無效的選項，請重新輸入。")

# 初始化
load_from_csv()  # Automatically loads this year's file like '2025_transactions.csv'
menu()
