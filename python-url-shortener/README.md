# SnapURL – Python URL Shortener

A sleek, full-featured URL shortener built with **Flask** and **SQLite**.

## ✨ Features

| Feature | Details |
|---|---|
| 🔗 URL Shortening | Instantly shorten any URL |
| 🎨 Custom Aliases | Choose your own short code (e.g. `/my-link`) |
| 📊 Click Analytics | Tracks every redirect with timestamp & IP |
| ⏱ Expiry Support | Set links to auto-expire after N days |
| 🔳 QR Code | Auto-generates a QR code for every link |
| 🗑 Delete Links | Remove any link via UI or API |
| 🌐 REST API | JSON API for programmatic access |

## 🚀 Quick Start

### 1. Create a virtual environment (recommended)

```bash
cd url-shortener
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📡 REST API Reference

### `POST /api/shorten`
Shorten a URL.

**Request body (JSON):**
```json
{
  "url": "https://example.com/very/long/path",
  "custom_code": "my-link",       // optional
  "expiry_days": 30               // optional
}
```

**Response:**
```json
{
  "short_url": "http://localhost:5000/my-link",
  "short_code": "my-link",
  "original": "https://example.com/very/long/path",
  "qr_code": "<base64-png>",
  "created_at": "2024-01-01T12:00:00",
  "expires_at": "2024-01-31T12:00:00"
}
```

---

### `GET /api/urls`
List all shortened URLs.

---

### `DELETE /api/urls/<short_code>`
Delete a shortened URL.

---

### `GET /api/urls/<short_code>/stats`
Get click stats for a specific link.

---

### `GET /<short_code>`
Redirects to the original URL (and records a click).

---

## 🗂 Project Structure

```
url-shortener/
├── app.py            # Flask app — routes, DB, API, HTML template
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── urls.db           # SQLite database (auto-created on first run)
```

## 🛠 Tech Stack

- **Python 3.8+**
- **Flask** – lightweight web framework
- **SQLite** – zero-config embedded database
- **qrcode + Pillow** – QR code generation
- **Vanilla JS + CSS** – dark-mode frontend (no frameworks)
