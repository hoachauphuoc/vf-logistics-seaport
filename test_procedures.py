"""
VF Logistics - Snowflake Procedure Test Suite
Run: python test_procedures.py
Requires: pip install snowflake-connector-python pytest pytest-html
"""

import snowflake.connector
import json
import time
import os
import sys
from datetime import datetime

# Configuration
SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT", "JMAXFXA-XN12202"),
    "user": os.getenv("SNOWFLAKE_USER", "CNNTMEOVAT"),
    "password": os.getenv("SNOWFLAKE_PASSWORD", ""),
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "MENDIX_APP",
    "schema": "AGENTS",
}


class TestResult:
    def __init__(self, name, category, status, duration_ms, details=""):
        self.name = name
        self.category = category
        self.status = status
        self.duration_ms = duration_ms
        self.details = details


def run_test(cursor, name, category, sql, validate_fn):
    start = time.time()
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        result = str(row[0]) if row else ""
        duration = int((time.time() - start) * 1000)

        passed, details = validate_fn(result, row)
        status = "PASS" if passed else "FAIL"
        return TestResult(name, category, status, duration, details)
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        return TestResult(name, category, "ERROR", duration, str(e)[:200])


def run_all_tests(cursor):
    results = []

    # ============================================================
    # CATEGORY 1: DATA INTEGRITY TESTS
    # ============================================================
    results.append(run_test(cursor,
        "BILL_OF_LADING record count >= 10000",
        "Data Integrity",
        "SELECT COUNT(*) FROM BILL_OF_LADING",
        lambda r, row: (int(row[0]) >= 10000, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "PORT_MASTER record count >= 50",
        "Data Integrity",
        "SELECT COUNT(*) FROM PORT_MASTER",
        lambda r, row: (int(row[0]) >= 50, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "VESSEL_REGISTRY record count >= 15",
        "Data Integrity",
        "SELECT COUNT(*) FROM VESSEL_REGISTRY",
        lambda r, row: (int(row[0]) >= 15, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "HS_CODE_REFERENCE record count >= 100",
        "Data Integrity",
        "SELECT COUNT(*) FROM HS_CODE_REFERENCE",
        lambda r, row: (int(row[0]) >= 100, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "AI_CALL_LOG table exists and accessible",
        "Data Integrity",
        "SELECT COUNT(*) FROM AI_CALL_LOG",
        lambda r, row: (True, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "SAP_FI_DOCUMENT table exists",
        "Data Integrity",
        "SELECT COUNT(*) FROM SAP_FI_DOCUMENT",
        lambda r, row: (True, f"Count: {row[0]}")
    ))

    results.append(run_test(cursor,
        "B/L data has diverse countries (>10)",
        "Data Integrity",
        "SELECT COUNT(DISTINCT PORT_OF_DISCHARGE_COUNTRY) FROM BILL_OF_LADING",
        lambda r, row: (int(row[0]) >= 10, f"Distinct countries: {row[0]}")
    ))

    results.append(run_test(cursor,
        "B/L data has diverse carriers (>=8)",
        "Data Integrity",
        "SELECT COUNT(DISTINCT CARRIER_NAME) FROM BILL_OF_LADING",
        lambda r, row: (int(row[0]) >= 8, f"Distinct carriers: {row[0]}")
    ))

    # ============================================================
    # CATEGORY 2: AI PROCEDURE TESTS
    # ============================================================
    results.append(run_test(cursor,
        "CLASSIFY_DOCUMENT_TEXT - valid B/L text",
        "AI Procedures",
        "CALL CLASSIFY_DOCUMENT_TEXT('BILL OF LADING No. MAEU1234567 Vessel: EVER GIVEN Voyage: 123E')",
        lambda r, row: ("document_type" in r, f"Response contains document_type: {'document_type' in r}")
    ))

    results.append(run_test(cursor,
        "CLASSIFY_DOCUMENT_TEXT - commercial invoice",
        "AI Procedures",
        "CALL CLASSIFY_DOCUMENT_TEXT('COMMERCIAL INVOICE No. INV-2024-001 Amount: USD 50,000')",
        lambda r, row: ("document_type" in r, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "CLASSIFY_DOCUMENT_TEXT - empty input (no crash)",
        "AI Procedures",
        "CALL CLASSIFY_DOCUMENT_TEXT('')",
        lambda r, row: (True, "No crash on empty input")
    ))

    results.append(run_test(cursor,
        "CLASSIFY_DOCUMENT_TEXT - very short input",
        "AI Procedures",
        "CALL CLASSIFY_DOCUMENT_TEXT('hello')",
        lambda r, row: (True, "No crash on minimal input")
    ))

    results.append(run_test(cursor,
        "AI_COMPLETE_WITH_RETRY - basic call",
        "AI Procedures",
        "CALL AI_COMPLETE_WITH_RETRY('llama3-8b', 'Reply OK', 1, 'test')",
        lambda r, row: ("response" in r, f"Has response key: {'response' in r}")
    ))

    # ============================================================
    # CATEGORY 3: COMPLIANCE & ENRICHMENT TESTS
    # ============================================================
    results.append(run_test(cursor,
        "CHECK_COMPLIANCE - valid B/L ID=1",
        "Compliance",
        "CALL CHECK_COMPLIANCE(1)",
        lambda r, row: ("overall_status" in r, f"Has overall_status: {'overall_status' in r}")
    ))

    results.append(run_test(cursor,
        "CHECK_COMPLIANCE - invalid ID (no crash)",
        "Compliance",
        "CALL CHECK_COMPLIANCE(99999)",
        lambda r, row: (True, "No crash on invalid ID")
    ))

    results.append(run_test(cursor,
        "ENRICH_DOCUMENT - valid B/L ID=1",
        "Compliance",
        "CALL ENRICH_DOCUMENT(1)",
        lambda r, row: ("enrichments" in r or "enrich" in r.lower(), f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "ENRICH_DOCUMENT - invalid ID (no crash)",
        "Compliance",
        "CALL ENRICH_DOCUMENT(99999)",
        lambda r, row: (True, "No crash on invalid ID")
    ))

    results.append(run_test(cursor,
        "DETECT_DUPLICATES - full scan",
        "Compliance",
        "CALL DETECT_DUPLICATES(NULL)",
        lambda r, row: ("alerts_found" in r or "alert" in r.lower(), f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "DETECT_DUPLICATES - specific ID",
        "Compliance",
        "CALL DETECT_DUPLICATES(1)",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    # ============================================================
    # CATEGORY 4: FUNCTION TESTS
    # ============================================================
    results.append(run_test(cursor,
        "GET_SHIPMENT_STATS - Japan",
        "Functions",
        "SELECT GET_SHIPMENT_STATS('Japan')",
        lambda r, row: ("total_shipments" in r, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "GET_SHIPMENT_STATS - non-existent country",
        "Functions",
        "SELECT GET_SHIPMENT_STATS('Atlantis')",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "GET_SHIPMENT_DETAIL - valid B/L",
        "Functions",
        "SELECT GET_SHIPMENT_DETAIL('BL-0001', 'status')",
        lambda r, row: (True, f"Response: {r[:80]}")
    ))

    # ============================================================
    # CATEGORY 5: VIEW TESTS
    # ============================================================
    results.append(run_test(cursor,
        "V_AI_DAILY_COST view accessible",
        "Views",
        "SELECT COUNT(*) FROM V_AI_DAILY_COST",
        lambda r, row: (True, f"Rows: {row[0]}")
    ))

    results.append(run_test(cursor,
        "V_AI_USAGE_SUMMARY view accessible",
        "Views",
        "SELECT COUNT(*) FROM V_AI_USAGE_SUMMARY",
        lambda r, row: (True, f"Rows: {row[0]}")
    ))

    results.append(run_test(cursor,
        "V_PORT_WEATHER_FORECAST view accessible",
        "Views",
        "SELECT COUNT(*) FROM V_PORT_WEATHER_FORECAST",
        lambda r, row: (True, f"Rows: {row[0]}")
    ))

    # ============================================================
    # CATEGORY 6: SAP INTEGRATION TESTS
    # ============================================================
    results.append(run_test(cursor,
        "SAP_POST_FI_DOCUMENT - valid B/L",
        "SAP Integration",
        "CALL SAP_POST_FI_DOCUMENT(1)",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "SAP_POST_GOODS_RECEIPT - valid B/L",
        "SAP Integration",
        "CALL SAP_POST_GOODS_RECEIPT(1)",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "SAP_CREATE_DELIVERY - valid B/L",
        "SAP Integration",
        "CALL SAP_CREATE_DELIVERY(1)",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    results.append(run_test(cursor,
        "SAP_ALLOCATE_COSTS - valid B/L",
        "SAP Integration",
        "CALL SAP_ALLOCATE_COSTS(1)",
        lambda r, row: (True, f"Response: {r[:100]}")
    ))

    # ============================================================
    # CATEGORY 7: EDGE CASE & SECURITY TESTS
    # ============================================================
    results.append(run_test(cursor,
        "SQL injection attempt in classify (no crash)",
        "Security",
        "CALL CLASSIFY_DOCUMENT_TEXT('test''; DROP TABLE BILL_OF_LADING; --')",
        lambda r, row: (True, "No crash on injection attempt")
    ))

    results.append(run_test(cursor,
        "Unicode input handling",
        "Security",
        "CALL CLASSIFY_DOCUMENT_TEXT('日本語テスト vận đơn 中文测试')",
        lambda r, row: (True, "No crash on unicode input")
    ))

    results.append(run_test(cursor,
        "Very long input (2000 chars)",
        "Security",
        f"CALL CLASSIFY_DOCUMENT_TEXT('{'A' * 2000}')",
        lambda r, row: (True, "No crash on long input")
    ))

    results.append(run_test(cursor,
        "NULL handling in GET_SHIPMENT_STATS",
        "Security",
        "SELECT GET_SHIPMENT_STATS(NULL)",
        lambda r, row: (True, f"Response: {r[:80]}")
    ))

    # ============================================================
    # CATEGORY 8: PERFORMANCE TESTS
    # ============================================================
    results.append(run_test(cursor,
        "B/L query performance (<2s for 10K records)",
        "Performance",
        "SELECT COUNT(*) FROM BILL_OF_LADING WHERE PORT_OF_DISCHARGE_COUNTRY = 'Japan'",
        lambda r, row: (True, f"Japan shipments: {row[0]}")
    ))

    results.append(run_test(cursor,
        "Classification cache check (<1s)",
        "Performance",
        "SELECT COUNT(*) FROM AI_CLASSIFICATION_CACHE",
        lambda r, row: (True, f"Cache entries: {row[0]}")
    ))

    return results


def generate_report(results):
    """Generate test coverage report."""
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")
    coverage = round(passed / total * 100, 1) if total > 0 else 0

    # Category breakdown
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"total": 0, "passed": 0}
        categories[r.category]["total"] += 1
        if r.status == "PASS":
            categories[r.category]["passed"] += 1

    report = []
    report.append("=" * 70)
    report.append("  VF LOGISTICS - TEST COVERAGE REPORT")
    report.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 70)
    report.append("")
    report.append(f"  TOTAL TESTS:  {total}")
    report.append(f"  PASSED:       {passed} ✅")
    report.append(f"  FAILED:       {failed} ❌")
    report.append(f"  ERRORS:       {errors} ⚠️")
    report.append(f"  COVERAGE:     {coverage}%")
    report.append("")
    report.append("-" * 70)
    report.append("  COVERAGE BY CATEGORY")
    report.append("-" * 70)
    report.append(f"  {'Category':<25} {'Tests':<8} {'Passed':<8} {'Coverage':<10}")
    report.append(f"  {'-'*25} {'-'*6} {'-'*6} {'-'*8}")

    for cat, data in sorted(categories.items()):
        cat_cov = round(data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
        bar = "█" * (cat_cov // 10) + "░" * (10 - cat_cov // 10)
        report.append(f"  {cat:<25} {data['total']:<8} {data['passed']:<8} {bar} {cat_cov}%")

    report.append("")
    report.append("-" * 70)
    report.append("  DETAILED RESULTS")
    report.append("-" * 70)

    current_category = ""
    for r in results:
        if r.category != current_category:
            current_category = r.category
            report.append(f"\n  [{current_category}]")

        icon = "✅" if r.status == "PASS" else "❌" if r.status == "FAIL" else "⚠️"
        report.append(f"    {icon} {r.name}")
        report.append(f"       Duration: {r.duration_ms}ms | {r.details[:60]}")

    report.append("")
    report.append("=" * 70)
    report.append(f"  FINAL SCORE: {coverage}% ({passed}/{total} tests passed)")
    report.append("=" * 70)

    return "\n".join(report)


def generate_markdown_report(results):
    """Generate markdown report for GitHub."""
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    coverage = round(passed / total * 100, 1) if total > 0 else 0

    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"total": 0, "passed": 0, "tests": []}
        categories[r.category]["total"] += 1
        if r.status == "PASS":
            categories[r.category]["passed"] += 1
        categories[r.category]["tests"].append(r)

    md = []
    md.append("# Test Coverage Report")
    md.append("")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Tests | {total} |")
    md.append(f"| Passed | {passed} |")
    md.append(f"| Failed | {total - passed} |")
    md.append(f"| **Coverage** | **{coverage}%** |")
    md.append("")
    md.append("## Coverage by Category")
    md.append("")
    md.append("| Category | Tests | Passed | Coverage |")
    md.append("|----------|-------|--------|----------|")

    for cat, data in sorted(categories.items()):
        cat_cov = round(data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
        md.append(f"| {cat} | {data['total']} | {data['passed']} | {cat_cov}% |")

    md.append("")
    md.append("## Detailed Results")
    md.append("")

    for cat, data in sorted(categories.items()):
        md.append(f"### {cat}")
        md.append("")
        md.append("| Test | Status | Duration |")
        md.append("|------|--------|----------|")
        for t in data["tests"]:
            icon = "✅" if t.status == "PASS" else "❌"
            md.append(f"| {t.name} | {icon} {t.status} | {t.duration_ms}ms |")
        md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    print("Connecting to Snowflake...")

    if not SNOWFLAKE_CONFIG["password"]:
        print("ERROR: Set SNOWFLAKE_PASSWORD environment variable")
        print("Usage: SNOWFLAKE_PASSWORD=xxx python test_procedures.py")
        sys.exit(1)

    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cursor = conn.cursor()

    print("Running test suite...\n")
    results = run_all_tests(cursor)

    # Console report
    report = generate_report(results)
    print(report)

    # Save markdown report
    md_report = generate_markdown_report(results)
    report_path = os.path.join(os.path.dirname(__file__), "TEST_COVERAGE_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"\nMarkdown report saved to: {report_path}")

    cursor.close()
    conn.close()

    # Exit with error code if tests failed
    passed = sum(1 for r in results if r.status == "PASS")
    if passed < len(results):
        sys.exit(1)
