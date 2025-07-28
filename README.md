# 🧾 Bookkeeping
 This project involves the development and customization of a personal bookkeeping application designed for use on both computers and smartphones. While primarily intended for practice and personal use, the project also serves as a platform for experimenting with and adopting new and advanced technologies to enhance development skills.

---

## 📌 專案特色

本專案為一個個人記帳應用程式，採用前端 React (或純 HTML/CSS/Tailwind) 作為使用者介面，後端使用 FastAPI 處理商業邏輯，並將資料儲存於 Google Drive。此架構兼顧開發效率與擴展彈性，適合個人或小型專案使用。

- ✅ 支援資料寫入 Google Drive，雲端儲存資料
- ✅ 可查詢記帳歷史，實用性高
- ✅ 支援圓餅圖 / 長條圖報表（使用 Chart.js / Recharts）
- ✅ 可部署到 Vercel、Netlify 或 GitHub Pages

---

## 📈 預期功能清單
1. 輸入收支（收入、支出、轉帳）
2. 顯示歷史紀錄（依時間排序）
3. 圓餅圖：分類支出分布
4. 長條圖：每月收支統計
5. Google OAuth 登入（進階）
6. 雙向同步（將 Drive 上的資料變動反映到畫面）

---

## 功能流程
1. 使用者在前端輸入記帳資料（類別、金額、日期、備註等）
2. 前端將資料透過 HTTP POST 請求送至 FastAPI 後端 API
3. FastAPI 執行邏輯運算（驗證資料格式、計算統計等）
4. FastAPI 透過 Google API 將資料存入指定試算表
5. 使用者查詢記帳紀錄時，前端發起 GET 請求，FastAPI 從 Google Drive 上讀取資料並回傳
6. 前端接收資料並以表格或圖表呈現

---

## 🔧 使用技術

| 元件     | 技術與工具                           | 功能說明               |
| ------ | ------------------------------- | ------------------ |
| 前端     | React + Tailwind CSS            | 使用者輸入介面與資料顯示       |
| 後端     | FastAPI                         | API 服務，處理邏輯與與資料操作  |
| 資料庫    | Google Drive                   | 儲存及讀取記帳資料          |
| API 認證 | Google Service Account + OAuth2 | 安全存取 Google Drive |

---

## 📁 專案架構

```yaml
bookkeeper/
├── main.py           ← 進入點：執行 CLI 選單
│
└── data/
    ├── csv/
    └── xlsx/
```

---

## 📦 部署建議
1. 前端：可使用 Vercel、Netlify 等免費靜態網站部署平台
2. 後端：可部署於 Render、Railway 等免費雲端服務（注意睡眠限制）
3. Google Drives：設定 Service Account 並授予試算表權限，確保後端能安全存取

## 🔐 注意事項
* Google Drives 適合小規模資料與簡單應用，若資料量大或複雜，建議使用正式資料庫
* 部署免費後端平台多數會有睡眠限制，首次請求會有延遲，屬正常現象
* Google API 需要妥善管理 OAuth2 認證資訊與 Service Account 金鑰，避免權限外洩
* 建議前端做基本資料驗證，提高使用者體驗與資料正確性

## 未來擴展方向
* 新增使用者登入與權限管理功能
* 使用正式資料庫（如 PostgreSQL）取代 Google Drives
* 增加資料分析與圖表功能
* 加入通知、匯出報表等附加功能

## 🙋‍♂️ 作者 Ludwig
* 國立中央大學 資工系畢業
* 熱愛 AI、深度學習、全端開發
* 專案初衷：訓練全端架構能力，做出自己會用的產品

## 📜 License
MIT License
