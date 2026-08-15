"""Automated tests for login_app.html based on login_test_cases.csv."""
 
import csv
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
 
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright is required. Install it with:")
    print("  pip install playwright")
    print("  python -m playwright install chromium")
    sys.exit(1)
 
SCRIPT_DIR = Path(__file__).resolve().parent
HTML_PATH = SCRIPT_DIR / "login_app.html"
CSV_PATH = SCRIPT_DIR / "login_test_cases.csv"
REPORT_PATH = SCRIPT_DIR / "test_report.html"
 
VALID_USERNAME = "admin"
VALID_PASSWORD = "test123"
REGISTERED_EMAIL = "admin@example.com"
 
 
@dataclass
class TestResult:
    test_id: str
    description: str
    expected: str
    status: str
    actual: str
    priority: str = ""
 
 
def load_test_cases(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))
 
 
def save_test_cases(csv_path: Path, test_cases: list[dict]) -> None:
    fieldnames = [
        "Test Case ID",
        "Description",
        "Expected Result",
        "Priority",
        "Status",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_cases)
 
 
def open_login_page(page) -> None:
    page.goto(HTML_PATH.as_uri())
 
 
def get_login_message(page) -> str:
    message = page.locator("#login-message")
    if message.is_visible():
        return message.inner_text().strip()
    return ""
 
 
def get_forgot_message(page) -> str:
    message = page.locator("#forgot-message")
    if message.is_visible():
        return message.inner_text().strip()
    return ""
 
 
def open_forgot_password_view(page) -> None:
    open_login_page(page)
    page.locator("#show-forgot-password").click()
    page.locator("#forgot-password-view").wait_for(state="visible")
 
 
def is_field_invalid(page, field_id: str) -> bool:
    return page.evaluate(
        f"""() => {{
            const field = document.getElementById('{field_id}');
            return field ? !field.checkValidity() : false;
        }}"""
    )
 
 
def run_login_test(page, test_id: str) -> tuple[str, str]:
    open_login_page(page)
    page.locator("#username").fill("")
    page.locator("#password").fill("")
 
    if test_id == "TC-LOGIN-001":
        page.locator("#username").fill(VALID_USERNAME)
        page.locator("#password").fill(VALID_PASSWORD)
        page.locator("#login-form button[type='submit']").click()
        message = get_login_message(page)
        if "success" in message.lower() and "welcome" in message.lower():
            return "Pass", message
        return "Fail", message or "No success message displayed."
 
    if test_id == "TC-LOGIN-002":
        page.locator("#username").fill(VALID_USERNAME)
        page.locator("#password").fill("wrongpassword")
        page.locator("#login-form button[type='submit']").click()
        message = get_login_message(page)
        if "invalid username or password" in message.lower():
            return "Pass", message
        return "Fail", message or "No error message displayed."
 
    if test_id == "TC-LOGIN-003":
        page.locator("#password").fill(VALID_PASSWORD)
        page.locator("#login-form button[type='submit']").click()
        message = get_login_message(page)
        username_invalid = is_field_invalid(page, "username")
        if username_invalid and not message:
            return "Pass", "Login blocked by browser validation on empty username."
        return "Fail", message or "Form submitted without blocking empty username."
 
    if test_id == "TC-LOGIN-004":
        page.locator("#username").fill(VALID_USERNAME)
        page.locator("#login-form button[type='submit']").click()
        message = get_login_message(page)
        password_invalid = is_field_invalid(page, "password")
        if password_invalid and not message:
            return "Pass", "Login blocked by browser validation on empty password."
        return "Fail", message or "Form submitted without blocking empty password."
 
    if test_id == "TC-LOGIN-005":
        for _ in range(5):
            page.locator("#username").fill(VALID_USERNAME)
            page.locator("#password").fill("wrongpassword")
            page.locator("#login-form button[type='submit']").click()
        message = get_login_message(page)
        if "account is locked" in message.lower():
            return "Pass", message
        return "Fail", message or "No account lock message; feature not implemented."
 
    return "Skipped", "No automated test defined for this test case."
 
 
def run_forgot_password_test(page, test_id: str) -> tuple[str, str]:
    open_forgot_password_view(page)
    page.locator("#email").fill("")
 
    if test_id == "TC-FORGOT-001":
        page.locator("#email").fill(REGISTERED_EMAIL)
        page.locator("#forgot-password-form button[type='submit']").click()
        message = get_forgot_message(page)
        if "password reset link has been sent" in message.lower():
            return "Pass", message
        return "Fail", message or "No confirmation message displayed."
 
    if test_id == "TC-FORGOT-002":
        page.locator("#email").fill("unknown.user@example.com")
        page.locator("#forgot-password-form button[type='submit']").click()
        message = get_forgot_message(page)
        if "password reset link has been sent" in message.lower():
            return "Pass", message
        return "Fail", message or "No generic confirmation message displayed."
 
    if test_id == "TC-FORGOT-003":
        page.locator("#forgot-password-form button[type='submit']").click()
        message = get_forgot_message(page)
        if "email is required" in message.lower():
            return "Pass", message
        return "Fail", message or "No validation message for empty email."
 
    if test_id == "TC-FORGOT-004":
        page.locator("#email").fill("not-an-email")
        page.locator("#forgot-password-form button[type='submit']").click()
        message = get_forgot_message(page)
        if "enter a valid email address" in message.lower():
            return "Pass", message
        return "Fail", message or "No validation message for invalid email format."
 
    if test_id == "TC-FORGOT-005":
        return "Fail", "Expired reset link flow is not implemented in login_app.html."
 
    return "Skipped", "No automated test defined for this test case."
 
 
def run_test_case(page, test_case: dict) -> TestResult:
    test_id = test_case["Test Case ID"]
    description = test_case["Description"]
    expected = test_case["Expected Result"]
    priority = test_case.get("Priority", "")
 
    if test_id.startswith("TC-LOGIN-"):
        status, actual = run_login_test(page, test_id)
    elif test_id.startswith("TC-FORGOT-"):
        status, actual = run_forgot_password_test(page, test_id)
    else:
        status, actual = "Skipped", "Unknown test case type."
 
    return TestResult(
        test_id=test_id,
        description=description,
        expected=expected,
        status=status,
        actual=actual,
        priority=priority,
    )
 
 
def print_results(results: list[TestResult]) -> None:
    print("=" * 70)
    print("LOGIN APP AUTOMATED TEST RESULTS")
    print("=" * 70)
 
    for index, result in enumerate(results, start=1):
        print(f"\n{index}. {result.test_id} - {result.status}")
        print(f"   Description: {result.description}")
        print(f"   Expected:    {result.expected}")
        print(f"   Actual:      {result.actual}")
 
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    skipped = sum(1 for r in results if r.status == "Skipped")
 
    print("\n" + "=" * 70)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 70)
 
 
def generate_html_report(results: list[TestResult], report_path: Path) -> None:
    passed = sum(1 for r in results if r.status == "Pass")
    failed = sum(1 for r in results if r.status == "Fail")
    skipped = sum(1 for r in results if r.status == "Skipped")
    total = len(results)
    pass_rate = int((passed / total) * 100) if total > 0 else 0
    timestamp = datetime.now().strftime("%d %B %Y, %I:%M %p")
 
    rows = ""
    for index, result in enumerate(results, start=1):
        if result.status == "Pass":
            badge = '<span class="badge pass">PASS</span>'
        elif result.status == "Fail":
            badge = '<span class="badge fail">FAIL</span>'
        else:
            badge = '<span class="badge skipped">SKIPPED</span>'
 
        rows += f"""
        <tr>
            <td>{index}</td>
            <td><strong>{result.test_id}</strong></td>
            <td>{result.description}</td>
            <td>{result.expected}</td>
            <td>{result.actual}</td>
            <td><span class="priority {result.priority.lower()}">{result.priority}</span></td>
            <td>{badge}</td>
        </tr>"""
 
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, Helvetica, sans-serif; background: #f4f6f8; color: #1f2937; padding: 30px; }}
        .header {{ background: #1e3a5f; color: white; padding: 24px 32px; border-radius: 10px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 1.8rem; margin-bottom: 6px; }}
        .header p {{ font-size: 0.9rem; opacity: 0.8; }}
        .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
        .card {{ background: white; border-radius: 10px; padding: 20px 28px; flex: 1; min-width: 140px;
                 box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
        .card .number {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; }}
        .card .label {{ font-size: 0.85rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }}
        .card.pass .number {{ color: #059669; }}
        .card.fail .number {{ color: #dc2626; }}
        .card.skipped .number {{ color: #d97706; }}
        .card.total .number {{ color: #2563eb; }}
        .card.rate .number {{ color: #7c3aed; }}
        table {{ width: 100%; border-collapse: collapse; background: white;
                 border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        thead {{ background: #1e3a5f; color: white; }}
        th {{ padding: 14px 16px; text-align: left; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #f9fafb; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; }}
        .badge.pass {{ background: #d1fae5; color: #065f46; }}
        .badge.fail {{ background: #fee2e2; color: #991b1b; }}
        .badge.skipped {{ background: #fef3c7; color: #92400e; }}
        .priority {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; }}
        .priority.high {{ background: #fee2e2; color: #991b1b; }}
        .priority.medium {{ background: #fef3c7; color: #92400e; }}
        .priority.low {{ background: #d1fae5; color: #065f46; }}
        .footer {{ text-align: center; margin-top: 24px; font-size: 0.85rem; color: #9ca3af; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Execution Report</h1>
        <p>Application: Login App &nbsp;|&nbsp; Executed: {timestamp} &nbsp;|&nbsp; Tool: Playwright + Python</p>
    </div>
 
    <div class="summary">
        <div class="card total"><div class="number">{total}</div><div class="label">Total</div></div>
        <div class="card pass"><div class="number">{passed}</div><div class="label">Passed</div></div>
        <div class="card fail"><div class="number">{failed}</div><div class="label">Failed</div></div>
        <div class="card skipped"><div class="number">{skipped}</div><div class="label">Skipped</div></div>
        <div class="card rate"><div class="number">{pass_rate}%</div><div class="label">Pass Rate</div></div>
    </div>
 
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Test Case ID</th>
                <th>Description</th>
                <th>Expected Result</th>
                <th>Actual Result</th>
                <th>Priority</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
 
    <div class="footer">
        <p>Generated automatically by QA Automation Suite &copy; {datetime.now().year}</p>
    </div>
</body>
</html>"""
 
    with report_path.open("w", encoding="utf-8") as f:
        f.write(html)
 
 
def update_csv_statuses(test_cases: list[dict], results: list[TestResult]) -> None:
    result_map = {result.test_id: result.status for result in results}
    for test_case in test_cases:
        test_id = test_case["Test Case ID"]
        if test_id in result_map:
            test_case["Status"] = result_map[test_id]
 
 
def main() -> int:
    if not HTML_PATH.exists():
        print(f"Error: login page not found at {HTML_PATH}")
        return 1
 
    if not CSV_PATH.exists():
        print(f"Error: test cases file not found at {CSV_PATH}")
        return 1
 
    test_cases = load_test_cases(CSV_PATH)
    results: list[TestResult] = []
 
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
 
        for test_case in test_cases:
            print(f"\nRunning: {test_case['Test Case ID']} - {test_case['Description']}")
            results.append(run_test_case(page, test_case))
 
        browser.close()
 
    print_results(results)
    update_csv_statuses(test_cases, results)
    save_test_cases(CSV_PATH, test_cases)
    print(f"\nUpdated statuses in: {CSV_PATH}")
 
    generate_html_report(results, REPORT_PATH)
    print(f"HTML report generated: {REPORT_PATH}")
    webbrowser.open(REPORT_PATH.as_uri())
    print("Report opened in your browser!")
 
    failed = any(result.status == "Fail" for result in results)
    return 1 if failed else 0
 
 
if __name__ == "__main__":
    raise SystemExit(main())