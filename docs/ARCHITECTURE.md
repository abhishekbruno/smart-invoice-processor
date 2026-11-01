# Smart Invoice Processor — System Architecture & Design

This document details the architectural blueprints, technical data flows, database models, and design patterns utilized in the **Smart Invoice Processor**.

---

## 1. High-Level System Architecture

The application combines **Robotic Process Automation (RPA)**, **Deterministic Financial Modeling (SQL + Decimal)**, **Persistent Vector Retrieval (ChromaDB)**, and **Large Language Model Grounding (Google Gemini API)** within a unified multi-page Streamlit application.

```mermaid
flowchart TD
    subgraph Ingestion["1. Ingestion Channels"]
        UI["Streamlit Uploads (PDF)"]
        WATCH["Watchdog Folder Monitor (data/invoices/)"]
        GMAIL["Gmail RPA Service (OAuth 2.0 read-only)"]
    end

    subgraph Processing["2. Layered Extraction Pipeline"]
        VAL["Validation & Hash (SHA-256)"]
        L1["Level 1: PyMuPDF Text Extraction"]
        L2["Level 2: Deterministic Rule-Based Parser"]
        L3["Level 3: Gemini Structured JSON Fallback"]
        L4["Level 4: Tesseract OCR (Scanned Fallback)"]
    end

    subgraph Storage["3. Dual-Model Storage Tier"]
        SQLITE[("SQLite Database\n(invoices, items, rates, sync)")]
        CHROMA[("ChromaDB Vector Store\n(Sentence Transformers 384d)")]
    end

    subgraph Intelligence["4. Analytical & AI Layer"]
        ROUTER{"Query Router\n(SQL vs RAG vs Hybrid)"}
        SQL_ENG["Deterministic Financial Engine"]
        CURR["Currency Service\n(Frankfurter / ECB reference rates)"]
        RAG_ENG["Grounded RAG Pipeline\n(Gemini 2.5 Flash)"]
        REP["Report Service\n(CSV, Excel, ReportLab PDF)"]
    end

    subgraph UI_Layer["5. User Interface (Streamlit)"]
        DASH["Dashboard & Charts"]
        MGR["Invoice Manager & Duplicate Review"]
        QA["Ask AI Chatbot"]
        AUTO["Automation & Poller"]
        REPORTS["Reports Center"]
        CFG["Settings & Diagnostics"]
    end

    UI --> VAL
    WATCH --> VAL
    GMAIL --> VAL
    VAL --> L1 --> L2 --> L3
    L1 -.-> L4
    L2 --> SQLITE
    L2 --> CHROMA

    QA --> ROUTER
    ROUTER -->|Numerical / Totals| SQL_ENG
    ROUTER -->|Clauses / Line items| RAG_ENG
    ROUTER -->|Hybrid Analysis| SQL_ENG & RAG_ENG
    SQL_ENG --> CURR
    SQLITE --> SQL_ENG
    CHROMA --> RAG_ENG

    SQLITE --> DASH & MGR & REPORTS
    SQL_ENG --> DASH
    CURR --> DASH & REPORTS
```

---

## 2. Ingestion & Pre-Processing Pipeline

The application supports three ingestion entry points:

1. **Direct UI Upload:** User drags and drops PDF files into `pages/2_Upload_Invoices.py`.
2. **Watchdog Folder Monitor:** `core/folder_monitor.py` tracks changes in `data/invoices/` using system file events, running autonomously in a daemon thread.
3. **Gmail RPA Inbox Automation:** `core/gmail_sync_service.py` searches Gmail for supplier invoices using the Gmail API v1 with read-only scopes.

### Pre-Processing Workflow:
- **File Validation:** Validates file size ($\le 20\text{ MB}$ by default) and magic bytes (`%PDF-`).
- **Cryptographic Hashing:** Computes SHA-256 checksum over the raw bytes.
- **Stage 1 Hash Deduplication:** If the identical SHA-256 hash already exists in SQLite, ingestion skips reprocessing to ensure idempotency.

---

## 3. Layered PDF Extraction Strategy

```mermaid
flowchart LR
    PDF["Incoming PDF"] --> P1["Level 1: PyMuPDF"]
    P1 -->|Text extracted| P2["Level 2: Heuristic & Regex Parser"]
    P1 -->|Zero / Low text| OCR["Level 4: Tesseract OCR"]
    OCR --> P2
    P2 -->|High Confidence & Math Verified| DB["SQLite & ChromaDB"]
    P2 -->|Missing Fields or Uncertain| P3["Level 3: Gemini Structured JSON"]
    P3 -->|Pydantic & Consistency Checks| DB
```

1. **Level 1 — Native PDF Extraction (PyMuPDF):** Extracts clean page-by-page text streams and document metadata.
2. **Level 2 — Deterministic Rule-Based Parser:** Employs regex patterns and known vendor dictionaries to extract invoice numbers, vendor names, issue dates, due dates, currencies, line items, and financial amounts.
3. **Level 3 — Optional Gemini AI Structured Extraction:** When rule-based heuristics produce uncertain or missing fields, the system can consult Google Gemini with a strict JSON schema validated via Pydantic.
   - **Financial Consistency Constraint:** $Subtotal + Tax - Discount \approx Total$. If arithmetic consistency fails, the document is flagged for manual human review.
4. **Level 4 — Optional Scanned OCR (Tesseract):** For image-only PDFs, falls back to local Tesseract OCR if installed, without blocking ordinary text-based invoice workflows.

---

## 4. Two-Tier Duplicate Prevention Architecture

```mermaid
flowchart TD
    RAW["Raw Document Stream"] --> HASH["Compute SHA-256"]
    HASH --> STAGE1{"Stage 1:\nFile Hash Exists in DB?"}
    STAGE1 -->|Yes| SKIP["Skip File (Identical Hash Duplicate)"]
    STAGE1 -->|No| PARSE["Extract Structured Metadata"]

    PARSE --> NORM["Normalize Vendor Identity\n& Invoice Number"]
    NORM --> STAGE2{"Stage 2:\nLogical Duplicate Matching\n(Vendor + Inv # + Amount)"}
    STAGE2 -->|Match Found| FLAG["Insert with status='suspected_duplicate'\nis_duplicate=1\n(Excluded from spending aggregates)"]
    STAGE2 -->|Distinct| INSERT["Insert with status='processed'\nis_duplicate=0\n(Eligible for financial totals)"]
```

- **Stage 1 — Identical File Protection:** Protects against re-uploading the exact same PDF bytes.
- **Stage 2 — Logical Business Invoice Protection:** Prevents duplicate accounting entries when the same invoice is re-exported, scanned with a different scanner, or sent multiple times under different filenames. Records are **never deleted automatically**, preserving an auditable history in SQLite while safeguarding aggregate spending calculations.

---

## 5. Gmail RPA Inbox Automation Workflow

```mermaid
sequenceDiagram
    participant App as Smart Invoice Processor
    participant OAuth as Google OAuth 2.0
    participant Gmail as Gmail API v1
    participant DB as SQLite Database
    participant Watch as Watch Folder (data/invoices/)

    App->>OAuth: Request read-only token (InstalledAppFlow)
    OAuth-->>App: Access & Refresh Tokens (saved to config/token.json)
    App->>Gmail: users.messages.list(q='has:attachment filename:pdf')
    Gmail-->>App: List of matching message IDs
    loop For each message
        App->>Gmail: users.messages.get(id, format='full')
        Gmail-->>App: Message headers, MIME structure
        App->>App: Scan MIME parts recursively for PDF attachments
        alt Attachment Already Handled
            App->>DB: Log skipped_duplicate
        else New Attachment
            App->>Gmail: users.messages.attachments.get()
            Gmail-->>App: Base64URL encoded payload
            App->>App: Decode, sanitize filename, validate magic bytes (%PDF-)
            App->>Watch: Write sanitized PDF
            App->>DB: Record processed attachment & message
            App->>App: Invoke standard extraction pipeline
        end
    end
    App->>DB: Update sync history & account last_synced_at
```

---

## 6. ChromaDB Vector Store & Embedding Architecture

- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` produces dense 384-dimensional semantic vectors.
- **Document Chunking:** `core/document_chunker.py` segments each invoice into:
  - **Summary Chunk:** High-level metadata (vendor, dates, totals, customer, payment status).
  - **Line Item Chunks:** Distinct service or product line descriptions.
  - **Contextual Chunk:** Page-level text blocks for narrative terms and conditions.
- **Vector Database:** Persistent on-disk ChromaDB collection (`storage/chroma/`). Supports metadata filtering by invoice ID, vendor, and document hash.

---

## 7. Deterministic Query Routing & RAG Pipeline

```mermaid
flowchart TD
    QUERY["User Natural-Language Query"] --> ROUTER{"core/query_router.py\nClassification"}

    ROUTER -->|SQL: Aggregations, Spending, Totals| SQL_PATH["core/query_service.py\nDeterministic SQLite Queries"]
    ROUTER -->|RAG: Document explanations, Clauses| RAG_PATH["core/rag_pipeline.py\nChromaDB Vector Retrieval"]
    ROUTER -->|Hybrid: Specific vendor spending + details| HYBRID_PATH["Execute SQL Totals + Retrieve Vector Chunks"]

    SQL_PATH --> CURR_LOOKUP["Convert Currency via Frankfurter / ECB"]
    CURR_LOOKUP --> FORMAT["Format Markdown with Dollar Escaping"]

    HYBRID_PATH --> GEMINI["Google Gemini 2.5 Flash\n(Grounding Prompt with Verified Totals)"]
    RAG_PATH --> GEMINI

    GEMINI --> CITATIONS["Append Source Citations & Evidence Snippets"]
    FORMAT --> OUTPUT["Display in Streamlit Ask AI Page"]
    CITATIONS --> OUTPUT
```

### Deterministic Financial Safety Rule:
**Large Language Models are never allowed to perform independent financial arithmetic.**
All mathematical totals, expense comparisons, and invoice counts originate strictly from deterministic SQLite queries and Decimal-based currency conversions. The LLM is used exclusively for natural-language synthesis, explanations, and summarization grounded in verified facts.

---

## 8. Multi-Currency Conversion Architecture

- **API Provider:** Frankfurter API v2 (`api.frankfurter.dev`).
- **Reference Rates:** European Central Bank (ECB) daily reference rates.
- **Conversion Math:** Python `Decimal` with `ROUND_HALF_UP` to two decimal places.
- **Supported Currencies:** USD, EUR, GBP, and INR.
- **Two-Tier Caching:**
  - Fast in-memory dictionary cache.
  - Persistent SQLite table `exchange_rate_cache`.
- **Historical vs. Latest Modes:** Invoices can be valued using either historical rates on their issue dates or the latest available market rates.

---

## 9. Reporting Service Architecture

`core/report_service.py` provides certified report generation across 4 core business domains:
1. **Invoice Summary Report:** Comprehensive record register with original and converted valuations.
2. **Monthly Expense Report:** Month-by-month spending trends converted to reference currency.
3. **Vendor Spending Report:** Supplier expenditure breakdowns alongside excluded duplicate values.
4. **Duplicate Review Report:** Audit register of suspected and confirmed duplicates.

**Output Engines:**
- **CSV:** UTF-8 encoded comma-separated values.
- **Excel:** OpenPyXL multi-sheet workbooks (`.xlsx`).
- **PDF:** ReportLab document flow with table styles, alternating row backgrounds, and landscape pagination.


---

## 10. Multi-Client Full-Stack Architecture

To provide enterprise-grade access across desktop and mobile form factors, the Smart Invoice Processor implements a unified multi-tier architecture:

```mermaid
flowchart TD
    subgraph UI_Tier["Client Applications Tier"]
        WEB["React + TypeScript SPA\n(Vite 8, Tailwind v4, TanStack Query, Recharts)"]
        MOBILE["Flutter Android App\n(Material 3, Riverpod 2.5, GoRouter, fl_chart)"]
        STREAMLIT["Streamlit Portal\n(Local Explorer & Admin Dashboard)"]
    end

    subgraph API_Tier["Unified REST API Tier (FastAPI :8000)"]
        AUTH["CORS Middleware & Rate Limiting"]
        INV_EP["/api/invoices\n(CRUD, Document Streaming, Duplicates)"]
        ANA_EP["/api/analytics\n(KPI Summaries, Monthly Trends, Vendor Spend)"]
        CHAT_EP["/api/chat\n(Hybrid Query Router, Grounded Citations)"]
        AUTO_EP["/api/automation\n(Folder Watcher & Gmail RPA Polling)"]
        REP_EP["/api/reports\n(Streaming CSV, Excel .xlsx, ReportLab PDF)"]
        SET_EP["/api/settings\n(Currency Preferences & Vector Re-indexing)"]
    end

    subgraph Core_Tier["Python Core Business Logic Tier"]
        DB_SRV["core/database.py (SQLite WAL)"]
        RAG_SRV["core/rag_pipeline.py + core/query_service.py"]
        CURR_SRV["core/currency_service.py (ECB / Frankfurter)"]
        PARSER_SRV["core/invoice_parser.py (PyMuPDF + Heuristics + Gemini)"]
        RPA_SRV["core/folder_monitor.py + core/gmail_sync_service.py"]
    end

    subgraph Storage_Tier["Data Consistency Tier"]
        SQLITE_DB[("SQLite Database\n(storage/database/invoices.db)")]
        CHROMA_DB[("ChromaDB Vector Store\n(storage/chroma/)")]
        FILES_DIR[("File Storage\n(data/invoices/, storage/processed/)")]
    end

    WEB -->|HTTP JSON / REST| AUTH
    MOBILE -->|HTTP via ADB Reverse tunnel| AUTH
    AUTH --> INV_EP & ANA_EP & CHAT_EP & AUTO_EP & REP_EP & SET_EP

    INV_EP --> DB_SRV & PARSER_SRV
    ANA_EP --> CURR_SRV & DB_SRV
    CHAT_EP --> RAG_SRV
    AUTO_EP --> RPA_SRV
    REP_EP --> DB_SRV & CURR_SRV
    SET_EP --> DB_SRV

    STREAMLIT -.-> Core_Tier

    DB_SRV --> SQLITE_DB
    RAG_SRV --> CHROMA_DB
    PARSER_SRV --> FILES_DIR
```

### Shared Data Consistency & Cross-Platform Integrity
1. **Single Source of Truth:** All clients (React website, Flutter Android app, and Streamlit) connect to the exact same backend SQLite database and ChromaDB vector store.
2. **Deterministic Calculations:** All financial metrics and aggregations are computed exclusively on the backend in Python using exact `Decimal` precision; clients never calculate arithmetic locally.
3. **Audit Safety:** Invoices marked as duplicates or verified on mobile immediately reflect on the web dashboard and Streamlit portal without synchronization delay.

---

## 11. Physical Device Mobile Debugging Architecture

For real-world testing on a physical Android smartphone connected via USB:

```
[ Physical Android Phone ]
       |
  (Flutter App)
       |
  http://127.0.0.1:8000
       |
[ USB Cable (ADB) ]
  adb reverse tcp:8000 tcp:8000
       |
[ Windows Laptop ]
  FastAPI Server (0.0.0.0:8000)
       |
  SQLite & ChromaDB
```

1. **ADB Reverse Tunnel:** `adb reverse tcp:8000 tcp:8000` routes port 8000 on the Android device back through the USB cable to port 8000 on the Windows laptop.
2. **Cleartext Traffic Policy:** `android:usesCleartextTraffic="true"` is enabled in Android debug configuration to permit HTTP development traffic over the local loopback.
3. **Dynamic Base URL:** The Flutter app includes a runtime URL configurator in its Settings screen, supporting zero-rebuild switching between USB ADB reverse (`http://127.0.0.1:8000/api`) and Wi-Fi LAN IP (`http://192.168.x.x:8000/api`).
