"""
Configuration file for TestRail API and project settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


"""TestRail API configuration"""

# TestRail API settings
TESTRAIL_URL = os.getenv("TESTRAIL_URL", "https://your-domain.testrail.io")
TESTRAIL_USERNAME = os.getenv("TESTRAIL_USERNAME", "your-email@domain.com")
TESTRAIL_PASSWORD = os.getenv("TESTRAIL_PASSWORD", "your-api-key-or-password")

# Project settings
PROJECT_ID = int(os.getenv("TESTRAIL_PROJECT_ID", 1))
SUITE_ID = int(os.getenv("TESTRAIL_SUITE_ID", 1))
TARGET_SECTION_ID = int(os.getenv("TARGET_SECTION_ID", 1))

# API endpoints
API_BASE_URL = f"{TESTRAIL_URL}/api/v2"
