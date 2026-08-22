# QA Automation Suite — Login App

A complete test automation framework built with Python and Playwright, featuring a CI/CD pipeline on GitHub Actions.

## 🧪 About This Project

This project demonstrates end-to-end QA automation for a login web application. It was built to showcase modern test automation practices including automated test execution, HTML reporting, and continuous integration.

## 🛠️ Technologies Used

- **Python 3.12** — core programming language
- **Playwright** — browser automation and test execution
- **GitHub Actions** — CI/CD pipeline for automated testing
- **HTML/CSS/JavaScript** — login application under test
- **CSV** — test case management

## 📋 Test Coverage

### Login Feature
| Test Case | Description | Priority |
|---|---|---|
| TC-LOGIN-001 | Valid login with correct credentials | High |
| TC-LOGIN-002 | Invalid login with wrong password | High |
| TC-LOGIN-003 | Login with empty username | Medium |
| TC-LOGIN-004 | Login with empty password | Medium |
| TC-LOGIN-005 | Account lockout after 3 failed attempts | Low |

### Forgot Password Feature
| Test Case | Description | Priority |
|---|---|---|
| TC-FORGOT-001 | Password reset with valid email | High |
| TC-FORGOT-002 | Password reset with unregistered email | High |
| TC-FORGOT-003 | Password reset with empty email | Medium |
| TC-FORGOT-004 | Password reset with invalid email format | Medium |
| TC-FORGOT-005 | Expired reset link handling | Low |

## 🚀 How To Run

### Prerequisites
- Python 3.12 or higher
- pip package manager

### Installation

1. Clone the repository:

git clone https://github.com/shivneet-oss/qa-automation.git
cd qa-automation


2. Install Playwright:

pip install playwright
python -m playwright install chromium


3. Run the tests:

python test_runner.py


## 📊 Test Report

After running the tests, an HTML report is automatically generated and opens in your browser. It includes:

- Summary dashboard with Pass/Fail/Skipped counts
- Pass rate percentage
- Colour coded results per test case
- Priority indicators

## ⚙️ CI/CD Pipeline

Every commit to main automatically triggers the GitHub Actions pipeline which:

1. Sets up a fresh Linux environment
2. Installs Python and Playwright
3. Executes all 10 test cases
4. Reports Pass/Fail results

## 👤 Author

**Shivneet**  
QA Test Manager | 25 years experience  
Learning AI-assisted test automation

---
*Built with Python, Playwright and Claude AI assistance*