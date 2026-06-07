# 🔍 Discovery Agent

> **AI-Powered Enterprise System Discovery**  
> Aivar AI/ML Hiring Challenge — Level 1

---

## 📖 Project Overview

**Discovery Agent** is an intelligent document analysis tool that automatically identifies and catalogs every software system, tool, platform, and application mentioned across multiple document types. It uses **Google Gemini** to perform deep semantic analysis, returning a structured, production-ready inventory of enterprise systems — complete with criticality ratings, confidence scores, and actionable metadata.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Multi-format ingestion | PDF, TXT, PNG, JPG, JPEG, XLSX |
| 🤖 AI-powered extraction | Google Gemini 1.5 Flash for system detection |
| 📊 Structured inventory | 9-field JSON schema per discovered system |
| 🎯 Confidence scoring | Explicit (95–100), Inferred (70–90), Weak (<70) |
| 🏷️ Criticality classification | High / Medium / Low based on system category |
| ⚠️ Manual review flags | Auto-flagged when confidence < 70 |
| 🔍 Search & filter | By name, category, and criticality |
| 📥 Export | JSON and CSV download |
| 🎨 Color-coded UI | Green / Yellow / Red confidence indicators |

---

## 🏗️ Architecture

```
User Uploads Documents
        │
        ▼
┌───────────────────────────────────────────────┐
│              Text Extraction Layer             │
│  ┌─────────┐ ┌──────────┐ ┌────────────────┐  │
│  │pdfplumber│ │pytesseract│ │pandas/openpyxl │  │
│  │(PDF)    │ │(Images)  │ │(XLSX)          │  │
│  └─────────┘ └──────────┘ └────────────────┘  │
└───────────────────────────────────────────────┘
        │
        ▼  Merged text context
┌───────────────────────────────────────────────┐
│              Gemini Agent Layer                │
│  • Sends combined text to Gemini 1.5 Flash    │
│  • Structured JSON prompt engineering         │
│  • Confidence + criticality rule enforcement  │
└───────────────────────────────────────────────┘
        │
        ▼  List[SystemDict]
┌───────────────────────────────────────────────┐
│              Streamlit UI Layer                │
│  • KPI Dashboard                              │
│  • Filterable data table                      │
│  • JSON viewer                                │
│  • CSV / JSON download                        │
└───────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
discovery_agent/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore
├── README.md
│
├── extractors/               # Document text extraction modules
│   ├── __init__.py
│   ├── pdf_reader.py         # pdfplumber-based PDF extraction
│   ├── image_reader.py       # pytesseract OCR for images
│   ├── excel_reader.py       # pandas XLSX extraction
│   └── text_reader.py        # Plain text file reader
│
├── agents/                   # AI agent modules
│   ├── __init__.py
│   └── system_detector.py    # Gemini-powered system detection
│
├── utils/                    # Helper utilities
│   ├── __init__.py
│   └── helper.py             # Data transformation, KPIs, exports
│
└── outputs/                  # Downloaded results (gitignored)
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Tesseract OCR engine installed on your system
- A Google Gemini API key

### 1. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu / Debian:**
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```

**Windows:**  
Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki

---

### 2. Clone the repository

```bash
git clone https://github.com/your-username/discovery-agent.git
cd discovery-agent
```

---

### 3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

---

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_key_here
```

Get a free API key at: https://aistudio.google.com/app/apikey

---

## ▶️ Running the Project

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📸 Screenshots

| Dashboard | Results Table |
|---|---|
| *(KPI cards + file upload sidebar)* | *(Color-coded system inventory)* |

---

## 🧪 Testing with Sample Documents

Create a test text file `sample.txt` with content like:

```
Our company uses Salesforce as our primary CRM. All support tickets are managed 
via Jira Service Management. Finance runs on SAP S/4HANA and payments are 
processed through Stripe. The development team uses GitHub and communicates on Slack.
```

Upload it and click **Analyse Documents** to see the agent in action.

---

## 🔮 Future Improvements

- [ ] Support for DOCX and PowerPoint files
- [ ] Multi-language document support
- [ ] Integration graph / system dependency mapping
- [ ] Bulk processing via REST API endpoint
- [ ] Historical comparison between discovery runs
- [ ] CMDB auto-population via ServiceNow API
- [ ] Role-based access control for enterprise teams
- [ ] Persistent database storage (PostgreSQL)

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Streamlit** | Frontend UI framework |
| **Google Gemini 1.5 Flash** | AI system detection |
| **pdfplumber** | PDF text extraction |
| **pytesseract** | OCR for image files |
| **Pillow** | Image processing |
| **pandas + openpyxl** | Excel file parsing |
| **python-dotenv** | Environment variable management |

---

## 📜 License

MIT License — built for the Aivar AI/ML Hiring Challenge.
