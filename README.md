# 🛡️ LogSentinel

## AI-Powered Intelligent Web Log Analyzer

---

## 🚀 Quick Start

```bash
cd /home/user/LogSentinel
python run.py
```

**Open:** http://localhost:8000

---

## 🌐 Access Points

| Service | URL |
|---------|-----|
| 📊 Dashboard | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |
| ❤️ Health | http://localhost:8000/health |

---

## 📁 Project Structure

```
LogSentinel/
├── app/
│   ├── main.py              ← FastAPI + HTML frontend
│   ├── ingestion/           ← File reading + sampling
│   ├── detection/           ← Format detection + validation
│   ├── ai/                  ← AI assistant
│   ├── parsers/             ← Generic parser
│   ├── normalization/       ← Common schema
│   ├── analytics/           ← Traffic analytics
│   ├── security/            ← Rules + Risk scoring
│   ├── ml/                  ← ML anomaly detection
│   └── dashboard/
│       └── index.html       ← HTML/CSS/JS Frontend ⭐
├── data/raw/sample.log
├── requirements.txt
├── run.py
└── README.md
```

---

## 🎨 Frontend Features

### HTML/CSS/JS Dashboard:
- 🎯 Risk Score Gauge (0-100)
- 📈 Traffic Charts (Hourly + Daily)
- 🔒 Security Threats (SQL, XSS, Brute Force)
- 🤖 ML Anomalies
- 📊 Interactive Charts (Chart.js)
- 🎨 Modern Dark Theme
- 📱 Responsive Design

---

## 🔧 How It Works

```
LOG FILE → Sample → Detect → Parse → Normalize → Analytics + Security + ML → Risk → Dashboard
```

---

## 📦 Requirements

```
fastapi>=0.104.1
uvicorn>=0.24.0
pandas>=2.1.3
scikit-learn>=1.3.2
```

---

## 📄 License

Educational purposes.
