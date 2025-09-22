"""
Configuration file for TestRail API, Jira API, and project settings.
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# TestRail API configuration

# TestRail API settings
TESTRAIL_URL = os.getenv("TESTRAIL_URL", "https://you-forgot-to-set-this.testrail.io")
TESTRAIL_USERNAME = os.getenv(
    "TESTRAIL_USERNAME", "i-do-not-know@your-testrail-account.com"
)
TESTRAIL_PASSWORD = os.getenv(
    "TESTRAIL_PASSWORD", "what-is-your-testrail-api-key-or-password?"
)

# Project settings
PROJECT_ID = int(os.getenv("TESTRAIL_PROJECT_ID", "1"))
SUITE_ID = int(os.getenv("TESTRAIL_SUITE_ID", "1"))
TARGET_SECTION_ID = int(os.getenv("TARGET_SECTION_ID", "1"))

# API endpoint
API_BASE_URL = f"{TESTRAIL_URL}/api/v2"


# Jira API configuration

# Jira API settings
JIRA_URL = os.getenv("JIRA_URL", "https://you-forgot-to-set-this.atlassian.net")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "i-do-not-know@your-jira-account.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "what-is-your-jira-api-key-or-password?")
JIRA_TICKET_ID = os.getenv("JIRA_TICKET_ID", "what-is-the-jira-ticket-id-001")
