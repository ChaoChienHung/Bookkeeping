# Bookkeeping
 This project involves the development and customization of a personal bookkeeping application designed for use on both computers and smartphones. While primarily intended for practice and personal use, the project also serves as a platform for experimenting with and adopting new and advanced technologies to enhance development skills.

# 🧾 Personal Finance Web App (Serverless with Google Sheets)

一個無後端的記帳應用，使用純前端（React）技術建構，資料儲存在 Google Sheets，適合個人財務管理。透過 Google Apps Script 或 Google OAuth API 與 Sheet 溝通，實現記帳紀錄的新增、查詢與可視化。

---

## 📌 專案特色

- ✅ 無需後端伺服器，節省部署與維運成本
- ✅ 支援資料寫入 Google Sheet，雲端儲存資料
- ✅ 可查詢記帳歷史，實用性高
- ✅ 支援圓餅圖 / 長條圖報表（使用 Chart.js / Recharts）
- ✅ 可部署到 Vercel、Netlify 或 GitHub Pages

---

## 🔧 使用技術

| 層 | 技術 | 描述 |
|----|------|------|
| 前端 | React + Vite | SPA 實作 |
| UI 框架 | Tailwind CSS | 快速開發、美觀 |
| 資料儲存 | Google Sheets | 當作後端資料庫 |
| 傳輸方式 | Apps Script / Google Sheets API | 實現資料讀寫 |
| 部署 | Vercel / GitHub Pages | 部署靜態網站 |

---

## 📁 專案架構

web-app/
├── index.html
├── src/
│ ├── App.tsx # 主頁面元件
│ ├── components/
│ │ └── TransactionForm.tsx
│ │ └── TransactionList.tsx
│ └── utils/
│ └── sheets.ts # 封裝 Sheets API 請求
├── public/
│ └── assets/
└── README.md

yaml
複製
編輯

---

## 🚀 使用方式

### 方案一：使用 Google Apps Script 當 Web API

1. 建立 Google Sheet，命名為 `MyFinanceSheet`
2. 點「擴充功能 → Apps Script」，貼上以下代碼：

```js
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Transactions");
  const data = JSON.parse(e.postData.contents);
  sheet.appendRow([new Date(), data.type, data.amount, data.note]);
  return ContentService.createTextOutput("Success");
}
```
點「部署 → 部署為網頁應用程式」：

新版本名稱：v1

誰可以存取：任何人皆可使用

複製 Web App URL，前端可直接發送 fetch 請求：

```js
fetch('https://script.google.com/macros/s/your-script-id/exec', {
  method: 'POST',
  body: JSON.stringify({
    type: "expense",
    amount: 150,
    note: "午餐"
  })
});
```
方案二：使用 Google Sheets API + OAuth（進階）
適合中階使用者，有 OAuth 2.0 流程

建立 GCP 專案並啟用 Google Sheets API

設定 OAuth 憑證，允許使用者登入

在前端整合登入按鈕與 access token 管理

使用 gapi.client.sheets.spreadsheets.values.append() 寫入資料

📈 預期功能清單
 輸入收支（收入、支出、轉帳）

 顯示歷史紀錄（依時間排序）

 圓餅圖：分類支出分布

 長條圖：每月收支統計

 Google OAuth 登入（進階）

 雙向同步（將 Sheet 變動反映到畫面）

🔐 注意事項
請勿公開部署包含憑證的 Apps Script URL

若採用 OAuth + Sheets API，請做好 token 管理

若為多人使用，建議做權限機制（非此版本範圍）

📦 部署方式（Vercel）
註冊 Vercel

新增專案 → 指定 GitHub Repo

將 vite.config.ts 設為 base 路徑 /

部署完成後即可存取 https://your-project.vercel.app

🙋‍♂️ 作者 Ludwig
國立中央大學 資工系畢業

熱愛 AI、深度學習、全端開發

專案初衷：訓練全端架構能力，做出自己會用的產品

📜 License
MIT License

yaml
複製
編輯

---

這份 README 就像是一份 **專案說明書**，適合放到 GitHub repo 中，讓自己或其他人能一目瞭然你這個 App 的設計理念與使用方式。

如果你選擇的是方案一，我可以幫你補上範例前端頁面 + Apps Script。你需要我幫你建一份這樣的 starter 專案嗎？或者你想先從哪一段開始？
