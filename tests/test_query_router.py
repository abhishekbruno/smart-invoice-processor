import pytest
from core.query_router import QueryRouter, QueryType


def test_query_router_sql_classification():
    router = QueryRouter()

    # Numerical aggregations / comparisons
    d1 = router.route("What did we spend on AWS?")
    assert d1.query_type == QueryType.SQL

    d2 = router.route("Which vendor charged the highest amount?")
    assert d2.query_type == QueryType.SQL

    d3 = router.route("Compare spending between AWS and Google Cloud")
    assert d3.query_type == QueryType.SQL

    d4 = router.route("Show all invoices from Microsoft")
    assert d4.query_type == QueryType.SQL

    d5 = router.route("Which invoices are overdue?")
    assert d5.query_type == QueryType.SQL


def test_query_router_rag_classification():
    router = QueryRouter()

    # Semantic explanations and line item descriptions
    d1 = router.route("What services did AWS charge us for?")
    assert d1.query_type == QueryType.RAG

    d2 = router.route("Summarize the Microsoft invoices.")
    assert d2.query_type == QueryType.RAG

    d3 = router.route("Explain this invoice's line items.")
    assert d3.query_type == QueryType.RAG

    d4 = router.route("What does the consulting fee cover?")
    assert d4.query_type == QueryType.RAG

    d5 = router.route("Which invoices contain cloud storage charges?")
    assert d5.query_type == QueryType.RAG


def test_query_router_hybrid_classification():
    router = QueryRouter()

    d1 = router.route("How much did we spend on cloud hosting last quarter, and what services were included?")
    assert d1.query_type == QueryType.HYBRID

    d2 = router.route("Which vendor charged the most for infrastructure, and why?")
    assert d2.query_type == QueryType.HYBRID

    d3 = router.route("What did we spend on AWS and explain what services were billed?")
    assert d3.query_type == QueryType.HYBRID

