# Smart Invoice Processor — Local Setup & Installation Guide

This guide provides instructions to install, configure, and run the **Smart Invoice Processor** locally on Windows, macOS, or Linux.

---

## 1. Prerequisites

- **Python:** Version 3.11 or 3.12 (Python 3.12 recommended).
- **Git:** For cloning the repository.
- **Google Gemini API Key:** Free tier from [Google AI Studio](https://aistudio.google.com/).
- **(Optional) Tesseract OCR:** Required only for scanned image-only PDFs. Standard digital PDFs parse directly using PyMuPDF without OCR.
- **(Optional) Google Cloud OAuth Client:** Required only if using Gmail RPA inbox automation.

---

## 2. Installation Steps (Windows PowerShell)

### Step 1: Clone the Repository
```powershell
git clone <repository-url>
cd p1
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
*(On macOS/Linux: `source .venv/bin/activate`)*

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template configuration file:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your text editor and add your Google Gemini API key:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
APP_TIMEZONE=Asia/Kolkata
```

---

## 3. Generate Demonstration Invoices

Generate 12 fictional sample invoices in USD, EUR, GBP, and INR:
```powershell
python scripts/generate_sample_invoices.py
```
This populates `data/samples/` with realistic multi-currency test PDFs.

---

## 4. Launch the Application

Start the Streamlit application:
```powershell
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`.

---

## 5. (Optional) Gmail RPA Automation Setup

The application functions completely without Gmail. If you wish to enable automatic inbox scanning for invoice attachments:

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., `invoice-processor-demo`).
3. Enable the **Gmail API** in **APIs & Services > Library**.
4. Configure the **OAuth Consent Screen** (User Type: *External*, add your email as a *Test User*).
5. Create credentials:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Choose **Desktop app**.
   - Download the JSON credentials file.
6. Rename the downloaded file to `credentials.json` and place it in the `config/` folder:
   ```text
   config/credentials.json
   ```
7. Open the application, navigate to **🤖 Automation** or **⚙️ Settings**, and click **Authorize Gmail Account**.
8. A browser window will open asking you to grant read-only access (`gmail.readonly`) to download invoice attachments.

---

## 6. (Optional) Tesseract OCR Setup

For scanned image PDFs:

### Windows:
1. Download the Tesseract installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to `C:\Program Files\Tesseract-OCR\`.
3. In your `.env` file, enable OCR:
   ```ini
   OCR_ENABLED=true
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

### macOS:
```bash
brew install tesseract
```

### Ubuntu / Debian:
```bash
sudo apt-get install tesseract-ocr libtesseract-dev
```

---

## 7. Running Automated Tests

Run the test suite with pytest:
```powershell
pytest -v
```
All unit and integration tests run using mocks and do not require active Google API credentials or live internet connections.

