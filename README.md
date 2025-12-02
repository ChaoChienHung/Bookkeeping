# 🧾 Bookkeeping — Personal Finance App

This project is a personal bookkeeping application designed for both desktop and mobile use.  
Originally created for practice and experimentation, it also serves as a playground for adopting new technologies and improving full-stack development skills.

---

## 🧱 Project Architecture

```
 Web   -----\
       API Request → Server → Database
Mobile -----/
```

### Technology Stack

| Layer       | Technology                               | Purpose                                   |
|-------------|------------------------------------------|-------------------------------------------|
| Web Client  | Next.js, React                           | Browser-based UI                          |
| Mobile App  | Flutter                                  | Cross-platform mobile UI                  |
| Server API  | Python (FastAPI)                         | Business logic, validation, data routing  |
| Database    | SQLite, PostgreSQL, MySQL, MariaDB       | Persistent storage                        |

---

## 📌 Project Features

This project is a personal finance tracking application featuring a React-based frontend (or pure HTML/CSS/Tailwind), a FastAPI backend, and Google Drive as the storage layer.  
The architecture balances simplicity, flexibility, and speed—ideal for personal or small-scale use.

- ✅ Store records on Google Drive via API  
- ✅ Query and review transaction history  
- ✅ Display charts (pie charts & bar charts) using Chart.js / Recharts  
- ✅ Deployable to Vercel, Netlify, or GitHub Pages  

---

## 📈 Planned Features

1. Input transactions (income, expenses, transfers)  
2. View transaction history (sorted by time)  
3. Pie chart: spending categorized by type  
4. Bar chart: monthly income & expense summary  
5. Google OAuth login (advanced)  
6. Bidirectional sync (reflect Google Drive updates in UI)

---

## 🔄 Workflow Overview

1. User enters transaction data (category, amount, date, note, etc.)  
2. Frontend sends an HTTP POST request to the FastAPI backend  
3. FastAPI validates the data and performs necessary logic  
4. Backend writes data to Google Sheets via Google API  
5. When users request history, the frontend sends a GET request  
6. FastAPI retrieves data from Google Drive and returns the results  
7. Frontend displays the data as tables or charts  

---

## 🔧 Tech Stack

| Component | Technologies / Tools                         | Description                           |
|----------|-----------------------------------------------|---------------------------------------|
| Frontend | React + Tailwind CSS                          | User interface & data visualization   |
| Backend  | FastAPI                                       | API services & business logic         |
| Storage  | Google Drive                                   | Data storage and retrieval            |
| Auth     | Google Service Account + OAuth2               | Secure access to Google Drive         |

---

## 📁 Project Structure

```yaml
bookkeeper/
├── main.py           # Entry point: CLI menu
│
└── data/
    ├── csv/
    └── xlsx/
```

## 📦 Deployment Recommendations

1. Frontend: Deploy on Vercel or Netlify
2.  Backend: Deploy on Render or Railway (note: may sleep on free tier)
3.  Google Drive: Configure Service Account and grant Spreadsheet access for secure operations

## 🔐 Notes & Considerations

- Google Drive is suitable for small datasets; for larger or complex workloads, consider PostgreSQL or other production databases
- Free-tier backend services may sleep when idle, causing slow first-time responses
- Handle OAuth2 credentials and Service Account keys securely
- Implement basic client-side validation for better UX and data accuracy

## 🚀 Future Expansion

- User authentication & access control
- Migrate to a production-grade database (e.g., PostgreSQL)
- Enhanced analytics & charting features
- Notifications, report export, and other advanced tools

## 🙋‍♂️ About the Author — Ludwig
- B.S. in Computer Science, National Central University
- Master in School of Computing, National University of Singapore
- Passionate about AI, deep learning, and full-stack development
- Motivation: build a complete, practical full-stack system for personal use

## 📜 License
MIT License
