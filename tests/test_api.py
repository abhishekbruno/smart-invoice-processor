import io
import pytest
from fastapi.testclient import TestClient
from api.main import app
from core.database import db

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert "timestamp" in data


def test_api_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"]["status"] == "online"
    assert "vector_store" in data
    assert "ai_service" in data


def test_api_list_invoices():
    response = client.get("/api/invoices")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert "total" in data
    assert data["page"] == 1


def test_api_get_invoice_detail_and_404():
    invoices = db.get_all_invoices()
    if invoices:
        target_id = invoices[0]["id"]
        response = client.get(f"/api/invoices/{target_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == target_id
        assert "vendor_name" in data
        assert "line_items" in data
        assert isinstance(data["line_items"], list)

    # Test non-existent ID
    response_404 = client.get("/api/invoices/999999")
    assert response_404.status_code == 404


def test_api_list_duplicates():
    response = client.get("/api/invoices/duplicates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_analytics_summary():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_spending" in data
    assert "total_invoices" in data
    assert "display_currency" in data
    assert data["display_currency"] in ["INR", "USD", "EUR", "GBP"]


def test_api_analytics_monthly():
    response = client.get("/api/analytics/monthly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "month" in data[0]
        assert "converted_spent" in data[0]


def test_api_analytics_vendors():
    response = client.get("/api/analytics/vendors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "vendor" in data[0]
        assert "converted_spent" in data[0]


def test_api_analytics_currencies():
    response = client.get("/api/analytics/currencies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "currency" in data[0]
        assert "converted_total" in data[0]


def test_api_analytics_expenses():
    response = client.get("/api/analytics/expenses")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "monthly_spending" in data
    assert "vendor_spending" in data
    assert "currency_distribution" in data


def test_api_chat_status():
    response = client.get("/api/chat/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured_model" in data
    assert "total_indexed_chunks" in data
    assert "unique_invoices_indexed" in data


def test_api_chat_query_sql():
    response = client.post(
        "/api/chat/query",
        json={"query": "What is our total spending?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "query_type" in data
    assert isinstance(data["citations"], list)


def test_api_automation_status():
    response = client.get("/api/automation/status")
    assert response.status_code == 200
    data = response.json()
    assert "folder_monitor_active" in data
    assert "gmail_configured" in data


def test_api_automation_history():
    response = client.get("/api/automation/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_reports_invoices_csv():
    response = client.get("/api/reports/invoices?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "filename=" in response.headers.get("content-disposition", "")


def test_api_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "preferred_display_currency" in data["data"]
    assert "latest_reference_rates_usd" in data["data"]

    # Test updating preferred currency
    update_res = client.post("/api/settings/currency", json={"currency": "USD"})
    assert update_res.status_code == 200
    update_data = update_res.json()
    assert update_data["success"] is True
    assert update_data["data"]["preferred_display_currency"] == "USD"

    # Reset back to INR
    client.post("/api/settings/currency", json={"currency": "INR"})


def test_api_verify_invoice():
    invoices = db.get_all_invoices()
    if invoices:
        target_id = invoices[0]["id"]
        response = client.post(f"/api/invoices/{target_id}/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "verified"
