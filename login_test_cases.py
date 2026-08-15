"""Print and export formatted login and forgot password test cases."""

import csv
from pathlib import Path

CSV_FILENAME = "login_test_cases.csv"

LOGIN_TEST_CASES = [
    {
        "id": "TC-LOGIN-001",
        "description": "Log in with valid username and password",
        "expected": "User is redirected to the dashboard and a welcome message is displayed.",
        "priority": "High",
        "status": "Not Executed",
    },
    {
        "id": "TC-LOGIN-002",
        "description": "Log in with an incorrect password",
        "expected": "Login fails and an error message 'Invalid username or password' is shown.",
        "priority": "High",
        "status": "Not Executed",
    },
    {
        "id": "TC-LOGIN-003",
        "description": "Log in with an empty username field",
        "expected": "Login is blocked and a validation message 'Username is required' is shown.",
        "priority": "Medium",
        "status": "Not Executed",
    },
    {
        "id": "TC-LOGIN-004",
        "description": "Log in with an empty password field",
        "expected": "Login is blocked and a validation message 'Password is required' is shown.",
        "priority": "Medium",
        "status": "Not Executed",
    },
    {
        "id": "TC-LOGIN-005",
        "description": "Log in with a locked account after multiple failed attempts",
        "expected": "Login is denied and an error message 'Account is locked. Try again later.' is shown.",
        "priority": "Low",
        "status": "Not Executed",
    },
]

FORGOT_PASSWORD_TEST_CASES = [
    {
        "id": "TC-FORGOT-001",
        "description": "Request password reset with a valid registered email address",
        "expected": "A confirmation message is shown and a password reset link is sent to the email.",
        "priority": "High",
        "status": "Not Executed",
    },
    {
        "id": "TC-FORGOT-002",
        "description": "Request password reset with an unregistered email address",
        "expected": "A generic confirmation message is shown without revealing whether the email exists.",
        "priority": "High",
        "status": "Not Executed",
    },
    {
        "id": "TC-FORGOT-003",
        "description": "Request password reset with an empty email field",
        "expected": "Request is blocked and a validation message 'Email is required' is shown.",
        "priority": "Medium",
        "status": "Not Executed",
    },
    {
        "id": "TC-FORGOT-004",
        "description": "Request password reset with an invalid email format",
        "expected": "Request is blocked and a validation message 'Enter a valid email address' is shown.",
        "priority": "Medium",
        "status": "Not Executed",
    },
    {
        "id": "TC-FORGOT-005",
        "description": "Reset password using an expired reset link",
        "expected": "Reset fails and an error message 'This reset link has expired' is shown.",
        "priority": "Low",
        "status": "Not Executed",
    },
]

ALL_TEST_CASES = LOGIN_TEST_CASES + FORGOT_PASSWORD_TEST_CASES

CSV_HEADERS = [
    "Test Case ID",
    "Description",
    "Expected Result",
    "Priority",
    "Status",
]


def print_test_cases(test_cases, title="TEST CASES"):
    """Print test cases in a numbered, formatted layout."""
    print("=" * 60)
    print(title)
    print("=" * 60)

    for index, case in enumerate(test_cases, start=1):
        print(f"\n{index}. Test Case ID: {case['id']}")
        print(f"   Description:     {case['description']}")
        print(f"   Expected Result: {case['expected']}")
        print(f"   Priority:        {case['priority']}")
        print(f"   Status:          {case['status']}")

    print("\n" + "=" * 60)
    print(f"Total test cases: {len(test_cases)}")
    print("=" * 60)


def print_all_test_cases():
    """Print login and forgot password test cases in separate sections."""
    print_test_cases(LOGIN_TEST_CASES, "LOGIN FEATURE - TEST CASES")
    print()
    print_test_cases(FORGOT_PASSWORD_TEST_CASES, "FORGOT PASSWORD FEATURE - TEST CASES")
    print(f"\nGrand total: {len(ALL_TEST_CASES)} test cases")


def export_to_csv(test_cases, filename=CSV_FILENAME):
    """Export test cases to a CSV file next to this script."""
    output_path = Path(__file__).resolve().parent / filename

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()

        for case in test_cases:
            writer.writerow(
                {
                    "Test Case ID": case["id"],
                    "Description": case["description"],
                    "Expected Result": case["expected"],
                    "Priority": case["priority"],
                    "Status": case["status"],
                }
            )

    return output_path


if __name__ == "__main__":
    print_all_test_cases()
    csv_path = export_to_csv(ALL_TEST_CASES)
    print(f"\nExported to: {csv_path.resolve()}")
