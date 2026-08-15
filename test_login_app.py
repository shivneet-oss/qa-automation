"""Automated tests for login_app.html based on login_test_cases.csv."""

import csv
import sys
from dataclasses import dataclass
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
    """Run a single login test case and return (status, actual_result)."""
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
        return (
            "Fail",
            message or "No account lock message; feature not implemented in login_app.html.",
        )

    return "Skipped", "No automated test defined for this test case."


def run_forgot_password_test(page, test_id: str) -> tuple[str, str]:
    """Run a single forgot password test case and return (status, actual_result)."""
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
        return (
            "Fail",
            "Expired reset link flow is not implemented in login_app.html.",
        )

    return "Skipped", "No automated test defined for this test case."


def run_test_case(page, test_case: dict) -> TestResult:
    test_id = test_case["Test Case ID"]
    description = test_case["Description"]
    expected = test_case["Expected Result"]

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

    passed = sum(1 for result in results if result.status == "Pass")
    failed = sum(1 for result in results if result.status == "Fail")
    skipped = sum(1 for result in results if result.status == "Skipped")

    print("\n" + "=" * 70)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("=" * 70)


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
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        for test_case in test_cases:
            results.append(run_test_case(page, test_case))

        browser.close()

    print_results(results)
    update_csv_statuses(test_cases, results)
    save_test_cases(CSV_PATH, test_cases)
    print(f"\nUpdated statuses in: {CSV_PATH}")

    failed = any(result.status == "Fail" for result in results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
