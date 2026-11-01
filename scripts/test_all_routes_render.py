import subprocess
import sys

routes = [
    ('/', ['Intelligent Workspace', 'Eligible spending', 'Processing Logs']),
    ('/invoices', ['Invoice Repository', 'Repository Ledger']),
    ('/upload', ['Upload Invoice', 'Ingestion Hub', 'Drag invoice PDF here']),
    ('/chat', ['Conversational RAG Intelligence', 'Gemini 2.5 Flash', 'CHROMA']),
    ('/analytics', ['Financial Insights', 'Treasury Telemetry', 'Run-Rate']),
    ('/automation', ['Ingestion Control Center', 'Robotic Process Automation']),
    ('/reports', ['Financial Reports', 'Audit & Ledger Reports']),
    ('/settings', ['Settings & Preferences', 'System Parameters', 'Visual Effects']),
]

all_passed = True
for path, expected_tokens in routes:
    url = f'http://localhost:5173{path}'
    res = subprocess.run(
        ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', '--headless=new', '--virtual-time-budget=3500', '--dump-dom', url],
        capture_output=True,
        text=True,
        timeout=15,
    )
    dom = res.stdout
    missing = [token for token in expected_tokens if token.lower() not in dom.lower()]
    if missing:
        print(f"FAIL: {path} missing tokens: {missing}")
        all_passed = False
    else:
        print(f"PASS: {path} verified (DOM size: {len(dom)} bytes, tokens: {expected_tokens})")

if not all_passed:
    sys.exit(1)
print("\nALL 8 ROUTES VERIFIED SUCCESSFULLY IN CHROME!")
