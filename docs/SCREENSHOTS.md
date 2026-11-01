# Smart Invoice Processor — Application Tour & Interface Guide

This document illustrates the user interface, navigation flow, and visual layouts of the **Smart Invoice Processor**.

---

## 1. Main Landing Page & System Health (`app.py`)
- **Header & Metrics:** Displays total invoices ingested, cleanly processed records, items requiring review, and verified records.
- **RPA Watcher Status:** Real-time badge indicating whether the filesystem watchdog daemon is monitoring `data/invoices/`.
- **Quick Navigation:** One-click shortcuts to the Financial Dashboard, Ask AI, RPA Automation, and Reports Center.
- **Recent Invoices Table:** Summary of the last 5 documents processed.

---

## 2. Financial & Extraction Dashboard (`pages/1_Dashboard.py`)
- **Preferred Display Currency:** Dropdown selector (INR, USD, EUR, GBP) dynamically revaluing all foreign invoices.
- **Valuation Mode:** Radio toggle switching between historical exchange rates (as of the invoice date) and latest reference rates.
- **Converted Spending Banner:** Displays the total eligible non-duplicate spending in INR with ECB reference rate transparency.
- **Interactive Visualizations:**
  - *Monthly Spending Bar Chart:* Plotly chart displaying monthly expenses converted to INR.
  - *Currency Distribution Pie Chart:* Share of total organizational spending by original invoice currency.
  - *Vendor Spending Horizontal Chart:* Top suppliers ranked by total expenditure.
  - *Document Processing Status:* Distribution of cleanly processed, needs review, verified, and suspected duplicate records.
- **Highest-Value Invoices:** Top 5 invoices highlighting original and converted INR amounts.

---

## 3. Upload Invoices (`pages/2_Upload_Invoices.py`)
- **Drag-and-Drop Ingestion:** Accepts single or batch PDF uploads with real-time size and format validation.
- **Instant Extraction Preview:** Displays parsed vendor name, invoice reference number, dates, currency, and financial amounts.
- **Human-in-the-Loop Verification:** Enables operators to manually adjust extracted numbers or line items before committing to SQLite and ChromaDB.

---

## 4. Invoice Manager & Duplicate Review (`pages/3_Invoice_Manager.py`)
- **Audit Table:** Filterable grid of all invoice records with search by vendor, status, or date range.
- **Duplicate Review Drawer:** Highlights suspected duplicate submissions flagged by Stage 2 logical matching.
- **Operator Actions:**
  - *Mark as Genuine:* Re-classifies a false positive as verified and includes it in spending calculations.
  - *Confirm Duplicate:* Confirms the duplicate flag, keeping the record safely archived for audit without double-counting expenses.

---

## 5. Ask AI & RAG Interface (`pages/4_Ask_AI.py`)
- **Hybrid Query Router:**
  - Aggregations and mathematical questions (e.g., *"How much did we spend on AWS in INR?"*) execute via deterministic SQL calculations.
  - Semantic and qualitative queries (e.g., *"What services did Twilio bill for?"*) retrieve relevant vector chunks from ChromaDB.
- **Grounded AI Answers:** Google Gemini 2.5 Flash formats natural-language explanations with verified financial facts.
- **Verified Source Citations:** Every AI answer includes document filenames, invoice numbers, vendor names, and evidence snippets.
- **Currency Valuation Badges:** Clear exchange rate, effective date, and European Central Bank source attribution.

---

## 6. RPA & Pipeline Automation (`pages/5_Automation.py`)
- **Gmail OAuth 2.0 Integration:** Connect, test, and disconnect your Google account with read-only scopes.
- **Sync Now:** Manually trigger an on-demand scan of your Gmail inbox for supplier invoices.
- **Periodic Poller:** Background thread executing automatic synchronization every 15 minutes.
- **Local Watchdog Monitor:** Start and stop the real-time `data/invoices/` directory watcher.
- **ChromaDB Reindexing:** One-click re-indexing of unindexed documents into the vector store.
- **Audit Logs:** Searchable history of processing events with execution times and error traces.

---

## 7. Financial & Audit Reports (`pages/7_Reports.py`)
- **Report Tabs:**
  1. *Invoice Summary Report:* Full register with original and converted valuations.
  2. *Monthly Expenses Report:* Monthly totals, vendor summaries, and eligible invoice counts.
  3. *Vendor Spending Report:* Verified vendor expenses alongside excluded duplicate allocations.
  4. *Duplicate Review Report:* Detailed log of all flagged duplicate submissions.
- **Download Engines:**
  - 📥 **Download CSV**
  - 📊 **Download Excel (.xlsx)**
  - 📄 **Download PDF** (formatted landscape report via ReportLab)

---

## 8. Settings & Diagnostics (`pages/6_Settings.py`)
- **Storage Diagnostics:** Path inspection for watch directory, processed archive, SQLite database, and ChromaDB directory.
- **Currency Preferences:** Set default display currency and view cached European Central Bank daily reference rates.
- **Vector Diagnostics:** Sentence Transformers model status and ChromaDB collection metrics.
- **Gemini API Diagnostics:** Live API connectivity check and model fallback verification.
- **OCR Diagnostics:** Automatic detection of the local Tesseract OCR engine.

